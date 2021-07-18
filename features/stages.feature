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

  Scenario: when a stage project is completed the fund are released
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And a stage was created with title "My third potato salad" and goal 350
    And user with mail "gracedoe@gmail.com" is authenticated and has a wallet
    And user with mail "gracedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When the seer "gracedoe@gmail.com" complete the stage 1
    Then stages are complete up to stage 1

  Scenario: when a more than one stages project are completed the funds are released
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And a stage was created with title "My third potato salad" and goal 350
    And user with mail "gracedoe@gmail.com" is authenticated and has a wallet
    And user with mail "gracedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When the seer "gracedoe@gmail.com" complete the stage 2
    Then stages are complete up to stage 2

  Scenario: when a more than one stages project are completed the funds are released
    Given user with mail "johndoe@gmail.com" is authenticated
    And a new project was created by the user with title "Potato salad"
    And a stage was created with title "My first potato salad" and goal 150
    And a stage was created with title "My second potato salad" and goal 100
    And a stage was created with title "My third potato salad" and goal 350
    And user with mail "gracedoe@gmail.com" is authenticated and has a wallet
    And user with mail "gracedoe@gmail.com" has a seer role
    And the owner of the project "johndoe@gmail.com" enabled the project for funding
    When the seer "gracedoe@gmail.com" complete the stage 2
    And the seer "gracedoe@gmail.com" complete the stage 1
    Then operation is rejected with the message "This stage was already released!"
