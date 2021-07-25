Feature: reviews
  Background: Created users and projects
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet

  Scenario: new project does not have any reviews
    Given user with mail "gracedoe@gmail.com" is authenticated
    When user views their profile
    Then it should include their wallet's address

  Scenario: a project with created stages can be started for funding
    When the owner of the project "johndoe@gmail.com" enables the project for funding
    Then the project state is "FUNDING"
    And user "janedoe@gmail.com" is supervising 1 project as seer

  Scenario: a project in funding stage can be invested in by one funder
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    Then the project state is "FUNDING"
    And the project invested ammount is 120 and has 1 investors

  Scenario: a project in funding stage can't be invested in if the funder does not have funds
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" does not have enough funds but invests 120
    Then operation is rejected with the message "Unable to fund project! Insufficient funds!"
    And the project state is "FUNDING"
    And the project invested ammount is 0 and has 0 investors

  Scenario: a project in funding stage can't be invested in if the payments service is down
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When payment service is down but user "peterdoe@gmail.com" invests 120
    Then operation is rejected with the message "Unable to fund project! Payments service is down!"
    And the project state is "FUNDING"
    And the project invested ammount is 0 and has 0 investors

  Scenario: a project in funding stage can be invested in by one funder, more than once
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "peterdoe@gmail.com" invests 50
    Then the project state is "FUNDING"
    And the project invested ammount is 170 and has 1 investors


  Scenario: a project in funding stage can be invested in by two funders
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 50
    Then the project state is "FUNDING"
    And the project invested ammount is 170 and has 2 investors


  Scenario: a project in funding stage can be invested over the goal
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    Then the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors


  Scenario: a project in funding stage can have have its funds withdrawn
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "peterdoe@gmail.com" withdraws 15
    Then the project state is "FUNDING"
    And the project invested ammount is 105 and has 1 investors


  Scenario: a project in "in progress" stage cannot be fund
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    And user "peterdoe@gmail.com" invests 15
    Then operation is rejected with the message "The project is not in funding state!"
    And the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors

  Scenario: a project in "in progress" stage cannot have its funds withdrawn
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    And user "peterdoe@gmail.com" withdraws 15
    Then operation is rejected with the message "The project is not cancelled or in funding state!"
    And the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors
