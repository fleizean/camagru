function likeImage(image_id, action) {
    console.log(image_id);
    console.log(action);
    const likeCount = document.getElementById(`like-count-${image_id}`);
    const likeIcon = document.getElementById(`like-icon-${image_id}`);

    fetch("/like_post/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            id: image_id,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (action === "like") {
            likeIcon.style.color = "red";
            likeCount.innerHTML = parseInt(likeCount.innerHTML) + 1;   
            const likeButton = document.getElementById(`like-image-${image_id}`);     
            likeButton.style.display = "none";
            const unlikeButton = document.getElementById(`unlike-image-${image_id}`);
            unlikeButton.style.display = "block";   
        }
        else if (action === "unlike") {
            likeIcon.style.color = "white";
            likeCount.innerHTML = parseInt(likeCount.innerHTML) - 1;
            const likeButton = document.getElementById(`like-image-${image_id}`);     
            likeButton.style.display = "block";
            const unlikeButton = document.getElementById(`unlike-image-${image_id}`);
            unlikeButton.style.display = "none";
        }
    });
}