Feature: stats

  Scenario: total users registered
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    When the stats are listed
    Then the total users should be 4

  Scenario: total seers registered
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And user with mail "johndoe@gmail.com" has a seer role
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    When the stats are listed
    Then the total seers should be 2

  Scenario: total projects registered
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a new project was created by the user with title "Potato salad 2"
    And a new project was created by the user with title "Potato salad 3"
    When the stats are listed
    Then the total projects should be 3

  Scenario: total favorites registered
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And the user favorited the project
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And the user favorited the project
    And the user unfavorited the project
    And a new project was created by the user with title "Potato salad 2"
    And user with mail "carladoe@gmail.com" is authenticated and has a wallet
    And the user favorited the project
    And user with mail "jackdoe@gmail.com" is authenticated and has a wallet
    And the user favorited the project
    When the stats are listed
    Then the total favorites should be 3

  Scenario: total investments registered
    Given user with mail "johndoe@gmail.com" is authenticated and has a wallet
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And user with mail "peterdoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" is authenticated and has a wallet
    And user with mail "janedoe@gmail.com" has a seer role
    And user with mail "carldoe@gmail.com" is authenticated and has a wallet
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When user "peterdoe@gmail.com" invests 120
    And user "carldoe@gmail.com" invests 50
    And the stats are listed
    Then the total investments should be 2

  Scenario: total hashtags registered
    Given user with mail "johndoe@gmai.com" is authenticated
    And a new project was created by the user with hashtags "green,world"
    And a new project was created by the user with hashtags "green,now"
    When the stats are listed
    Then the total hashtags should be 3

