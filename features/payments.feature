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
