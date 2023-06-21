// Script for read notification button
$(document).ready(() => {
    $('.notification-read').on('click', (event) => {
        event.preventDefault();

        const notificationReadLink = $(event.currentTarget);
        // Get request url
        const notificationReadUrl = notificationReadLink.data('href');
        const notificationCountElement = $('#notification-count');

        // Send request to update information
        $.ajax({
            url: notificationReadUrl,
            type: 'GET',
            success: function (response) {

                // Delete read button
                notificationReadLink.remove();

                // Update counter
                if (response.unread_notification_count === 0) {
                    notificationCountElement.remove();
                } else {
                    notificationCountElement.text(response.unread_notification_count);
                }
            }
        });
    });
});

// Script for delete notification button
$(document).ready(() => {
    $('.notification-delete').on('click', (event) => {
        event.preventDefault();

        const notificationDeleteLink = $(event.currentTarget);
        // Get request url
        const notificationDeleteUrl = notificationDeleteLink.data('href');
        // Get notification id
        const notificationId = notificationDeleteLink.data('notification-id');
        const unreadNotificationCountElement = $('#notification-count');
        const notificationTable = $('#notification-table');
        // Get specific row id
        const notificationRow = $(`#notification-${notificationId}`);

        // Send request to update information
        $.ajax({
            url: notificationDeleteUrl,
            type: 'GET',
            success: function (response) {

                // Update unread notification count
                if (response.unread_notification_count === 0) {
                    unreadNotificationCountElement.remove();
                } else {
                    unreadNotificationCountElement.text(response.unread_notification_count);
                }
                // Update notification table
                if (response.notification_count === 0) {
                    const p = document.createElement("p");
                    p.textContent = 'No notifications';
                    notificationTable.replaceWith(p);
                } else {
                    notificationRow.remove();
                }
            }
        })
    });
});