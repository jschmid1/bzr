Feature: Query for one specific basegood 
  Scenario: Retrieve a basegoods details
      Given some basegoods are in the system
      Then I retrieve the basegoods 1
      Then I should get a 200 response
      Then the following basegood details are returned:
           | name | initprice | id 
           | Iron | 42.1       | 1

Scenario: Query for a invalid basegood id
      Given some basegoods are in the system
      Then I retrieve the basegoods 666
      Then I should get a 404 response
