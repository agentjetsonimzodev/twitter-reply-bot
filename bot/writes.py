"""Tweet posting via tweepy (official X API, OAuth 1.0a user-context).

TODO (Phase 3):
  - OAuth 1.0a client init from stored tokens
  - post_reply(tweet_id, text) -> response with new tweet ID
  - Handle 429: read x-rate-limit-reset, sleep until reset
  - Monthly write counter (refuse if at/near 1500)
"""
