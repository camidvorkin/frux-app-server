Feature: payments

  Scenario: registered user was assigned a wallet
    Given user with mail "johndoe@gmail.com" is authenticated
    When user views their profile
    Then it should include their wallet's address

  # Scenario: a project with created stages can be started for funding
  #   Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
  #   And a new project was created by the user with title "Potato salad"
  #   And user with mail "janedoe@gmail.com" is authenticated and has a wallet
  #   And user with mail "janedoe@gmail.com" has a seer role
