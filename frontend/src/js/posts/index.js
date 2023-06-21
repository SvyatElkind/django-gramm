// Script for post like/unlike and total like count
$(document).ready(() => {
    const postLikeLink = $('#like-post');
    const postLikesCountElement = $('#post-likes-count');
    const likeIconElement = $('#like-icon');

    postLikeLink.on('click', (event) => {
        event.preventDefault();

        const postLikeUrl = postLikeLink.data('href');

        objectLikeUnlike(postLikeUrl, postLikesCountElement, likeIconElement);
    });
});

// Script for image like/unlike and total like count
$(document).ready(() => {
    $('.like-image').on('click', (event) => {
        event.preventDefault();

        const imageLikeLink = $(event.currentTarget);
        // Get request url
        const imageLikeUrl = imageLikeLink.data('href');

        // Extract the image id from the element's data attribute
        const imageId = imageLikeLink.data('image-id');

        // Construct the id of the elements using the image ID
        const imageLikesCountElement = $(`#image-likes-count-${imageId}`);
        const likeIconElement = $(`#image-like-icon-${imageId}`);

        objectLikeUnlike(imageLikeUrl, imageLikesCountElement, likeIconElement)
    });
});

// Function sends request to like/unlike object and
// update html elements
function objectLikeUnlike(url, likesCountElement, likeIconElement) {
    $.ajax({
        url: url,
        type: 'GET',
        success: function (response) {
            likesCountElement.text(response.likes_count);
            if (response.liked) {
                likeIconElement.removeClass('bi-heart').addClass('bi-heart-fill');
            } else {
                likeIconElement.removeClass('bi-heart-fill').addClass('bi-heart');
            }
        },
    });
}

