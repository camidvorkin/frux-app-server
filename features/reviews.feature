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
    When the project's reviews are listed
    Then the project has 0 reviews and a general score of 0

  Scenario: two seeders review the project
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    And user "peterdoe@gmail.com" invested 120
    And user "carldoe@gmail.com" invested 120
    When user "peterdoe@gmail.com" reviews the project with score 4.5 and description "This is the best project ever!"
    And user "carldoe@gmail.com" reviews the project with score 1.5 and description "I'm very disappointed..."
    And the project's reviews are listed
    Then the project has 2 reviews and a general score of 3

  Scenario: a user who did not seed the project cannot review it
    Given the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" reviews the project with score 4.5 and description "This is the best project ever!"
    Then operation is rejected with the message "Only investors of the project can add reviews!"
