// Script for follow/unfollow user
$(document).ready(() => {
    const followUserLink = $('#follow-user');

    followUserLink.on('click', (event) => {
        event.preventDefault();

        // Get request url
        const followUserUrl = followUserLink.data('href');
        const followersCountElement = $('#followers');

        // Send request to update information
        $.ajax({
            url: followUserUrl,
            type: 'GET',
            success: function (response) {
                followUserLink.text(response.follow_status);
                followersCountElement.text(response.followers_count + " Followers");
            }
        });
    });
});