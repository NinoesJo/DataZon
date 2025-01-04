function toggleUpvote(reviewed_id, review_type, reviewer_id) {
    const button = document.getElementById(`upvote-btn-${reviewed_id}`);
    const upvoteCountSpan = document.getElementById(`upvote-count-${reviewed_id}`);
    const message = document.getElementById(`upvote-message-${reviewed_id}`);
    const isUpvote = button.textContent.trim() === "Upvote";

    // Send the request to the server with updated data
    const endpoint = isUpvote ? "/social/upvote" : "/social/remove_upvote";
    const data = { reviewer_id, reviewed_id: reviewed_id.split('-')[1], review_type };

    fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            message.style.display = "inline";
            button.style.display = "none";
            let currentCount = parseInt(upvoteCountSpan.textContent);
            upvoteCountSpan.textContent = isUpvote ? currentCount + 1 : Math.max(0, currentCount - 1);
            button.textContent = isUpvote ? "Remove Upvote" : "Upvote";
        } else {
            alert("An error occurred. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
}

function toggleDetails(id) {
    var row = document.getElementById(id);
    row.style.display = row.style.display === "none" || row.style.display === "" ? "table-row" : "none";
}