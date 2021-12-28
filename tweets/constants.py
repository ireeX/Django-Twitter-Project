class TweetPhotoStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2

# for better display on Django Admin site UI
TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'Pending'),
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)

TWEET_PHOTS_UPLOAD_LIMIT = 9