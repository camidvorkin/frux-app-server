Feature: hashtags

 Scenario: a new project is created with 3 hashtags
     Given user with mail "johndoe@gmai.com" is authenticated
     And a new project was created by the user with hashtags "new,project,art"
     When hashtags are listed
     Then get a list of 3 hashtags

 Scenario: two projects with similar hashtags
     Given user with mail "johndoe@gmai.com" is authenticated
     And a new project was created by the user with hashtags "green,world"
     And a new project was created by the user with hashtags "green,now"
     When hashtags and projects are counted
     Then get 3 hashtags and 2 projects
