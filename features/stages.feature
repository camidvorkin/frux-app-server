Feature: stages

  Scenario: a project with no stages has goal 0
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    When the project is listed
    Then the project's goal is 0

  Scenario: a project with one stage has the same goal as the stage itself
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    When the project is listed
    Then the project's goal is 150

  Scenario: a project has the same goal as the sum of the stages
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And a stage was created with title "My third potato salad" and goal 350
    When the project is listed
    Then the project's goal is 600
