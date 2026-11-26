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
