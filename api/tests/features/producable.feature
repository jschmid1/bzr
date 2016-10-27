Feature: Query for one specific 'producable'
Scenario: Retrieve a 'producables' details
Given some 'producables' are in the system
When I retrieve the 'producables' '1'
Then I should get a '200' response
And the following producable details are returned:
       | name | price | id 
       | Tool | 1.0   | 1

Scenario: Query for a invalid producable id
Given some 'producables' are in the system
When I retrieve the 'producables' '666'
Then I should get a '404' response
