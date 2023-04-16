# Senan Repo Overview

Senan is a Github repository that performs semantic analysis on Twitter data to create a short video. The repository
takes a query string and the number of tweets to be fetched as inputs. Once the tweets are fetched, the repository uses
the VADER Sentiment Analysis tool to perform semantic analysis on the tweets. Finally, the repository combines the
tweets and sentiment analysis results in a short video using the Moviepy library and uploads it to Youtube.

## Features

The Senan repository has the following features:

### Twitter API Integration

Senan uses the Twitter API to fetch tweets based on a specified query string and number of tweets. To use this feature,
the user must have a Twitter Developer Account and provide their authentication credentials in a separate Python file.

### Sentiment Analysis using VADER

Senan uses the VADER Sentiment Analysis tool to perform semantic analysis on the tweets. VADER (Valence Aware Dictionary
and Sentiment Reasoner) is a lexicon-based approach that works well on social media texts. The tool assigns scores to
each tweet based on how positive, negative, or neutral its meaning is. The VADER tool automatically recognizes and rates
sentiments in social media texts and can work effectively on texts with emojis, informal languages, or other stylistic
expressions.

### Video Creation and Upload to Youtube

Senan uses Moviepy, a popular video editing library for Python, to combine the tweets and sentiment analysis results
into a short video. Finally, the repository uploads the video to Youtube. For this feature to work, the user must have a
Youtube Developer Account and provide their authentication credentials in a separate Python file.

### Seaborn Visualization

In addition to the video, Senan also generates a visualization using the Seaborn library. Seaborn is a Python data
visualization library based on matplotlib that provides a high-level interface for drawing attractive statistical
graphics. The generated visualization provides additional insight into the sentiment analysis results.

## Installation

To install the Senan repository, follow the steps below:

### Clone the Repository

Clone the repository using the following command:

    git clone https://github.com/PhilTrigu/senan.git

### Install the Requirements

Install the requirements using the following command:

    pip install -r requirements.txt

### Create a Twitter Developer Account

Create a Twitter Developer Account by following the steps in the following link:

    https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api

Senan uses the Twitter API v1 with essential access only. Save your credentials in the .env file.

### Create a Youtube Developer Account

Create a Youtube Developer Account by following the steps in the following link:

    https://developers.google.com/youtube/registering_an_application

Senan uses Oauth2 authentication. Save your credentials in the .env file.

### Create an OpenAI account (optional)

Create an OpenAI account by following the steps in the following link:

    https://beta.openai.com/docs/developer-quickstart/overview

Save your credentials in the .env file.

## Usage

To use the Senan repository, follow the steps below:

    python main.py

## Output

The output of the Senan repository is a short video and a visualization. You will find the video and visualization in
the assets directory. The video will be uploaded to Youtube.


