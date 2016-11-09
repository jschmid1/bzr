Feature: User 1 attempts to produce a item
    Scenario: you have the not the right ammount of basegoods to produce something
        Given The system is set up properly
        Then I produce the producables 1
        Then I should get a 409 response
        And my buildqueue should not contain that producable 1

    Scenario: you have the the right ammount of basegoods to produce something
        Given The system is set up properly
        Then I buy all the needed basegoods for producable 1
        Then I produce the producables 1
        Then I should get a 200 response
        And my buildqueue should contain that producable 1
