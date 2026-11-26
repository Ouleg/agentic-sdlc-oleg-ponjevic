Feature: Execute a command sequence

  Scenario: Rover moves and turns to the expected final position
    Given the Rover Service is running
    And a 5 × 5 grid with no obstacles
    And the rover starts at (0, 0) heading N
    When I send POST /simulate with the JSON body
      """
      {"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 5, "height": 5, "obstacles": []}, "commands": "FFRFF"}
      """
    Then the response status is 200
    And the final position is (2, 2)
    And the final heading is E
    And the blocked list is empty

  Scenario: Empty command string leaves the rover where it started
    Given the Rover Service is running
    And a 5 × 5 grid with no obstacles
    And the rover starts at (3, 1) heading W
    When I send POST /simulate with commands ""
    Then the response status is 200
    And the final position is (3, 1)
    And the final heading is W
    And the blocked list is empty

  Scenario: Obstacle and boundary blocks are both reported and the run continues
    Given the Rover Service is running
    And a 3 × 3 grid with one obstacle at (1, 1)
    And the rover starts at (0, 1) heading E
    And the Command String is "FLFFRFF"
    When I send POST /simulate with the JSON body
      """
      {"start": {"x": 0, "y": 1, "heading": "E"}, "grid": {"width": 3, "height": 3, "obstacles": [{"x": 1, "y": 1}]}, "commands": "FLFFRFF"}
      """
    Then the response status is 200
    And the final position is (2, 2)
    And the final heading is E
    And the blocked list is exactly [{"index": 0, "reason": "obstacle"}, {"index": 3, "reason": "boundary"}]
    And the F commands at indices 5 and 6 are executed after the boundary block at index 3
