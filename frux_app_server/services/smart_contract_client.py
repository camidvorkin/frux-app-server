import json
import os

import requests

from frux_app_server.services.logger import logger


class SmartContractException(Exception):
    pass


class SmartContractClient:
    def __init__(self):
        self.url = os.environ.get('FRUX_SC_URL', 'http://localhost:3000')
        self.api_key = os.environ.get('FRUX_SC_API_KEY', '')

    def _request(
        self,
        path,
        expected_code=None,
        message='make request',
        func=requests.get,
        body=None,
    ):
        if not body:
            body = {}
        try:
            r = func(
                f'{self.url}{path}', json=body, headers={'x-api-key': self.api_key}
            )
        except requests.ConnectionError as e:
            logger.error('Unable to %s! Payments service is down!', message)
            raise SmartContractException(
                f'Unable to {message}! Payments service is down!'
            ) from e
        if r.status_code == 401:
            logger.error('Unable to %s! Invalid API key!', message)
            raise SmartContractException(f'Unable to {message}! Invalid API key!')
        if expected_code and r.status_code != expected_code:
            logger.error('Unable to %s! %s - %s', message, str(r.status_code), r.text)
            return SmartContractException(
                f'Unable to {message}! {r.status_code} - {r.text}'
            )

        res = json.loads(r.content.decode())
        res['_status_code'] = r.status_code
        res['_text'] = r.text

        return res

    def _validate_enough_funds(self, res):
        if res['_status_code'] != 200:
            if 'code' in res and res['code'] == 'INSUFFICIENT_FUNDS':
                raise SmartContractException(
                    'Unable to fund project! Insufficient funds!'
                )
            raise SmartContractException(
                f'Unable to fund project! {res["_status_code"]} - {res["_text"]}'
            )

    def wei_to_eth(self, wei_hex):
        return float.fromhex(wei_hex) / (10 ** 18)

    def create_user_wallet(self):
        '''
        Requests a new user wallet, returns a dictionary with the address and internal ID
        '''
        try:
            return self._request(
                '/wallet',
                expected_code=200,
                message='request wallet',
                func=requests.post,
            )
        except SmartContractException:
            return {}

    def get_wallet_balance(self, wallet_id):
        '''
        Returns the balance for a given wallet
        '''
        path = f'/wallet/{wallet_id}/balance'
        return self._request(path, expected_code=200, message='request balance')[
            'balance'
        ]

    def get_private_key(self, wallet_id):
        '''
        Returns the private key for a given wallet
        '''
        path = f'/wallet/{wallet_id}'
        return self._request(path, expected_code=200, message='request private key')[
            'privateKey'
        ]

    def invest_project(self, project_hash, funder_id, amount):
        '''
        Invests in the project with the given hash the amount of ETH for the funder with the given ID,
        returns the total invested amount
        '''
        body = {
            "funderId": funder_id,
            "amountToFund": amount,
        }
        path = f"/project/{project_hash}"

        res = self._request(path, message='fund project', func=requests.post, body=body)

        self._validate_enough_funds(res)

        invested_amount = self.wei_to_eth(res['value']['hex'])

        return invested_amount

    def withdraw_funds(self, project_hash, funder_id, amount):
        '''
        Withdraws funds invested in the project with the given hash the amount
        of ETH for the funder with the given ID.
        Returns the withdrawn fund amount.
        '''

        body = {'funderId': funder_id}

        if amount:
            body['fundsToWithdraw'] = amount

        self._request(
            f"/project/{project_hash}/withdraw",
            200,
            'withdraw funds',
            requests.post,
            body,
        )

        return amount

    def complete_stage(self, seer_id, project_hash, stage_index):
        '''
        Completes the stage with the given index in the project with the given hash.
        Returns the stage_index
        '''
        body = {"reviewerId": seer_id}
        res = self._request(
            f"/project/{project_hash}/stageId/{stage_index}",
            message='complete stage',
            func=requests.post,
            body=body,
        )
        self._validate_enough_funds(res)

        return stage_index

    def create_project_smart_contract(self, owner_id, reviewer_id, stages_cost):
        '''
        Creates a new smart contract for the owner, reviewer and related stages costs.
        Returns the transaction hash.
        '''
        body = {
            "ownerId": owner_id,
            "reviewerId": reviewer_id,
            "stagesCost": stages_cost,
        }

        res = self._request(
            "/project", message='create project', func=requests.post, body=body
        )

        return res['txHash']


smart_contract_client = SmartContractClient()
