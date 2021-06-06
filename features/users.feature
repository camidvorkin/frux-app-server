Feature: users

  Scenario: a new user is registered
     Given user is not registered
      When user registers with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      And image "image1" and location "-34.588363,-58.423254"
      Then user already registered with name "Pepe Suarez" and mail "pepe@fi.uba.ar"

  Scenario: user registers with an already used email
     Given user is already registered with name "Pepe Suarez", mail "pepe@fi.uba.ar", image "image2" and location "-34.588363,-58.423254"
      When user registers with name "Pepe Suarez" and mail "pepe@fi.uba.ar"
      And image "image2" and location "-34.588363,-58.423254"
      Then operation is rejected with the message "Email address already registered!"

  Scenario: register with an invalid email
     Given user is not registered
      When user registers with name "Pepe Suarez" and mail "pepe"
      And image "image3" and location "-34.588363,-58.423254"
      Then operation is rejected with the message "Invalid email address!"

  Scenario: list users
     Given user is already registered with name "Pepe Suarez", mail "pepe@fi.uba.ar", image "image4" and location "-34.588363,-58.423254"
       And user is already registered with name "Andrea Suarez", mail "andrea@fi.uba.ar", image "image4" and location "-34.588363,-58.423254"
      When users are listed
      Then get a list of 2 users

  Scenario: find user by id
     Given user is already registered with name "Pepe Suarez", mail "pepe@fi.uba.ar", image "image5" and location "-34.588363,-58.423254"
      And user is already registered with name "Andrea Suarez", mail "andrea@fi.uba.ar", image "image5" and location "-34.588363,-58.423254"
      When user with id 1 is listed
      Then get user with name "Pepe Suarez" and mail "pepe@fi.uba.ar"

  Scenario: update user information
     Given user is already registered with name "Pepe Suarez", mail "pepe@fi.uba.ar", image "image6" and location "-34.588363,-58.423254"
      When user update their username to "Pepito" and their image to "image7"
      Then the user's information change
