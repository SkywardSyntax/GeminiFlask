# GitHub Codespaces ♥️ Flask

Welcome to your shiny new Codespace running Flask! We've got everything fired up and running for you to explore Flask.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with the what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

To run this application:

```
flask --debug run
```

## Visual Improvements

We have made several visual improvements to the chat application to enhance its appearance and user experience.

### New Styles and Layout

- Updated the background color to a gradient for a more modern look.
- Added padding and margin to the chat messages for better spacing.
- Updated the button styles to be more visually appealing.
- Added hover effects to the buttons for better interactivity.
- Updated the font styles for a more modern look.

### Updated HTML Structure

- Updated the structure of the chat container for better layout.
- Added a header section with a logo or title for better branding.
- Updated the form structure for better alignment and spacing.
- Added a footer section with additional information or links.

### Screenshots

Here are some screenshots of the improved chat application:

![Chat Application Screenshot 1](screenshots/screenshot1.png)
![Chat Application Screenshot 2](screenshots/screenshot2.png)

## New Feature: Summary Generation

We have added a new feature to the chat application that allows users to generate a summary of their chat history.

### How to Use the Summary Generation Feature

1. Engage in a conversation with the chat model.
2. Once the model has responded, a "Generate Summary" button will appear below the chat form.
3. Click the "Generate Summary" button to request a summary of the chat history.
4. The summary will be generated using the Gemini API and displayed in the chat container.

### Technical Details

- The summary generation feature is implemented in `app.py`, `templates/index.html`, `static/main.css`, and `README.md`.
- A new route `/generate-summary` is added to handle summary generation requests.
- The Gemini API is used to generate a summary of the chat history.
- The summary is returned as a JSON response and displayed in the chat container.

### Screenshots

Here are some screenshots of the summary generation feature:

![Summary Generation Screenshot 1](screenshots/summary_screenshot1.png)
![Summary Generation Screenshot 2](screenshots/summary_screenshot2.png)
