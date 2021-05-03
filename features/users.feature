Feature: users

  Scenario: usuario se registra
     Given usuario no esta registrado
      When usuario se registra con nombre "Pepe Suarez" y mail "pepe@fi.uba.ar"
      Then usuario registrado con nombre "Pepe Suarez" y mail "pepe@fi.uba.ar"

  Scenario: usuario se registra con un mail repetido
     Given usuario ya se encuentra registrado con nombre "Pepe Suarez" y mail "pepe@fi.uba.ar"
      When usuario se registra con nombre "Pepe Suarez" y mail "pepe@fi.uba.ar"
      Then se rechaza la operacion con el mensaje "Email address already registered!"

  Scenario: usuario se registra con un mail invalido
     Given usuario no esta registrado
      When usuario se registra con nombre "Pepe Suarez" y mail "pepe"
      Then se rechaza la operacion con el mensaje "Invalid email address!"

  Scenario: listado de usuarios
     Given usuario ya se encuentra registrado con nombre "Pepe Suarez" y mail "pepe@fi.uba.ar"
       And usuario ya se encuentra registrado con nombre "Andrea Suarez" y mail "andrea@fi.uba.ar"
      When se listan todos los usuarios
      Then se obtienen 2 usuarios