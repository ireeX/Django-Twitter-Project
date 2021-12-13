# Project Introduction
This is a twitter-like project. You can signup and login to your account, 
perform post and view tweets, follow and unfollow your
friends. 

We use push mode (fanout on write) for newsfeed module.

## APIs:
| Functions                 | Method|URL                                                        |
|---------------------------|-------|-----------------------------------------------------------|
| Account Login             | POST  | http://localhost/api/accounts/login/                      |   
| Account Logout            | POST  | http://localhost/api/accounts/logout/                     |
| Check Account Status      | GET   | http://localhost/api/accounts/login_status/               |
| Account Register          | POST  | http://localhost/api/accounts/signup/                     |
| View Tweets               | GET   | http://localhost/api/tweets/?user_id={user_id}            |
| Post Tweet                | POST  | http://localhost/api/tweets/?user_id={user_id}            |
| Update Tweet              | PUT   | http://localhost/api/tweets/{tweet_id}/                    |
| Delete Tweet              | DELETE| http://localhost/api/tweets/{tweet_id}/                    |
| Retrieve Comment with Tweet| GET  | http://localhost/api/tweets/{tweet_id}/?is_preview={bool}  |
| View Followings           | GET   | http://localhost/api/friendships/{user_id}/followings/    |
| View Followers            | GET   | http://localhost/api/friendships/{user_id}/followers/     |    
| Follow                    | POST  | http://localhost/api/friendships/{user_id}/follow/        |
| Unfollow                  | POST  | http://localhost/api/friendships/{user_id}/unfollow/      |
| View Comment for A Tweet  | GET   | http://localhost/api/comments/?tweet_id={tweet_id}        |
| Post Comment              | POST  | http://localhost/api/comments/?tweet_id={tweet_id}        |
| Update Comment            | PUT   | http://localhost/api/comments/{comment_id}/               |
| Delete Comment            | DELETE| http://localhost/api/comments/{comment_id}/               |

