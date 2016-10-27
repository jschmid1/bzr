Feature: GET user by ID
Scenario: Query for a valid user
Given Some 'users' are in the system
When I retrieve the 'users' '1'
Then I should get a '200' response
And the following user details are returned:
       | name | balance |  id 
       | John | 42.2    |  1 

Scenario: Query for a invalid user id
Given some 'users' are in the system
When I retrieve the 'users' '666'
Then I should get a '404' response
 
