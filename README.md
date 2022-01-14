# Project Introduction
This is a twitter-like project. You can sign up and login to your account, 
perform post and view tweets, follow and unfollow your
friends. 

We use push mode (fanout on write) for newsfeed module.

## APIs:
| Functions                 | Method|URL                                        | Required Parameters       |
|---------------------------|-------|-------------------------------------------|---------------------------|
| Account Login             | POST  | /api/accounts/login/                      | username, password        |
| Account Logout            | POST  | /api/accounts/logout/                     |                           |
| Check Account Status      | GET   | /api/accounts/login_status/               |                           |
| Account Register          | POST  | /api/accounts/signup/                     | username, password, email |
| View Latest Tweets        | GET   | /api/tweets/?user_id={user_id}&created_at__gt={time} |                |
| View Previous Tweets      | GET   | /api/tweets/?user_id={user_id}&created_at__lt={time} |                |
| Post Tweet                | POST  | /api/tweets/?user_id={user_id}            | content                   |
| Update Tweet              | PUT   | /api/tweets/{tweet_id}/                   | content                   |
| Delete Tweet              | DELETE| /api/tweets/{tweet_id}/                   |                           |
| Retrieve Comment with Tweet| GET  | /api/tweets/{tweet_id}/?is_preview={bool} |                           |
| View Followings           | GET   | /api/friendships/{user_id}/followings/?page={page_number}    |        |
| View Followers            | GET   | /api/friendships/{user_id}/followers/?page={page_number}     |        |
| Follow                    | POST  | /api/friendships/{user_id}/follow/        |                           |
| Unfollow                  | POST  | /api/friendships/{user_id}/unfollow/      |                           |
| View Comment for A Tweet  | GET   | /api/comments/?tweet_id={tweet_id}        |                           |
| Post Comment              | POST  | /api/comments/?tweet_id={tweet_id}        | content                   |
| Update Comment            | PUT   | /api/comments/{comment_id}/               | content                   |
| Delete Comment            | DELETE| /api/comments/{comment_id}/               |                           |
| Like                      | POST  | /api/likes/                               | content type, object id   |
| Unlike                    | POST  | /api/likes/cancel/                        | content type, object id   |
| Notifications             | GET   | /api/notifications/                       |                           |
| Unread Notification Count | GET   | /api/notifications/unread-count/          |                           |
| Mark All As Read          | POST  | /api/notifications/mark-all-as-read/      |                           |
| Update Notifications      | PUT   | /api/notifications/{notification_id}/     | unread                    |

