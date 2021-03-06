Feature: User 1 attempts to buy a basegood
    Scenario: You have enough money
        Given The system is set up properly
        Then I record the current price for a basegood
        Then I buy the basegoods 1
        Then I should get a 200 response
        And my inventory should contain basegood 1
        And the connected producables should be more expensive
        And the price should be higher than before

     Scenario: You dont have enough money
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I spend all my money
        Then I buy the basegoods 1
        Then I should get a 409 response
        And my inventory should not contain basegood 1
        And the connected producables should have the same price
        And the price should be the same

      Scenario: The resource on the map has been depleted
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I make sure that the basegood 1 is not present on the map
        Then I make sure that I have enough money
        Then I buy the basegoods 1
        Then I expect "Resources exceeded on this map" in the message 
        Then I should get a 409 response
        And my inventory should not contain basegood 1
        And the connected producables should have the same price
        And the price should be the same
