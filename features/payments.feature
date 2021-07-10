Feature: payments

  Scenario: registered user was assigned a wallet
    Given user with mail "johndoe@gmail.com" is authenticated
    When user views their profile
    Then it should include their wallet's address

  Scenario: a project with created stages can be started for funding
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And a stage was created with title "My third potato salad" and goal 350
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    When the owner of the project "johndoe@gmail.com" enables the project for funding
    Then the project state is "FUNDING"
    And user "janedoe@gmail.com" is supervising 1 project as seer

  Scenario: a project in funding stage can be invested in by one funder
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    Then the project state is "FUNDING"
    And the project invested ammount is 120 and has 1 investors

  Scenario: a project in funding stage can be invested in by one funder, more than once
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "peterdoe@gmail.com" invests 50
    Then the project state is "FUNDING"
    And the project invested ammount is 170 and has 1 investors


  Scenario: a project in funding stage can be invested in by two funders
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 50
    Then the project state is "FUNDING"
    And the project invested ammount is 170 and has 2 investors


  Scenario: a project in funding stage can be invested over the goal
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    Then the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors


  Scenario: a project in funding stage can have have its funds withdrawn
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "peterdoe@gmail.com" withdraws 15
    Then the project state is "FUNDING"
    And the project invested ammount is 105 and has 1 investors


  Scenario: a project in "in progress" stage cannot be fund
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    And user "peterdoe@gmail.com" invests 15
    Then operation is rejected with the message "The project is not in funding state!"
    And the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors



  Scenario: a project in "in progress" stage cannot have its funds withdrawn
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 350
    And user "peterdoe@gmail.com" withdraws 15
    Then operation is rejected with the message "The project is not cancelled or in funding state!"
    And the project state is "IN_PROGRESS"
    And the project invested ammount is 250 and has 2 investors
