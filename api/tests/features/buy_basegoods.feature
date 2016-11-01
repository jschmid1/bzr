Feature: Attempt to buy a basegood
Scenario: You have enough money
Given some 'basegoods' are in the system
When I buy the 'basegoods' '1'
Then I should get a '200' response
And my inventory should contain that 'basegood' '1'

Scenario: You don't have enough money
Given some 'basegoods' are in the system but you don't have money
When I buy the 'basegoods' '1'
# For now.. later this should be a 401 or smth
Then I should get a '200' response
And my inventory should not contain that 'basegood'
