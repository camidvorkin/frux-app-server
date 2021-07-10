Feature: hashtags

  Scenario: a project was not marked as favorite by any user
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    When users who favorited the project are listed
    Then get a list of 0 favorites

  Scenario: a project was not marked as favorite by two users
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And user with mail "janedoe@gmali.com" is authenticated
    And the user favorited the project
    And user with mail "peterdoe@gmali.com" is authenticated
    And the user favorited the project
    When users who favorited the project are listed
    Then get a list of 2 favorites


  Scenario: a project which was unfavorited by a usesr is updated
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And user with mail "janedoe@gmali.com" is authenticated
    And the user favorited the project
    And user with mail "peterdoe@gmali.com" is authenticated
    And the user favorited the project
    And the user unfavorited the project
    When users who favorited the project are listed
    Then get a list of 1 favorites
