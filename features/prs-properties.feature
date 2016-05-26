Feature: Presentation properties
  In order to interact with a presentation
  As a developer using python-pptx
  I need read/write properties on the presentation object


  Scenario: Get Presentation.slide_width, .slide_height
    Given a presentation
     Then its slide width matches its known value
      And its slide height matches its known value


  Scenario: Set Presentation.slide_width, .slide_height
    Given a presentation
     When I change the slide width and height
     Then the slide width matches the new value
      And the slide height matches the new value


  Scenario: Presentation.slides
    Given a presentation
     Then prs.slides is a Slides object
