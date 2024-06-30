let search = document.getElementById("search");
let search_icon = document.getElementById("search_icon");
search_icon.addEventListener("click", function(){
  console.log("click");
  search.classList.toggle("show");
});


document.addEventListener("DOMContentLoaded", function() {
  // ID kullanarak input'a erişim
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener("input", function() {
      const query = this.value;

      fetch("/search_profiles/", { // Backend endpoint
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken") // CSRF token
          },
          body: JSON.stringify({ query: query })
      })
      .then(response => response.json())
      .then(data => {
        const searchResults = document.getElementById('searchResults');
        searchResults.innerHTML = '';
    
        // JSON stringini JavaScript dizisine dönüştür
        const profiles = JSON.parse(data.profiles);
    
        if (profiles.length > 0) {
            profiles.forEach(profile => {
                const fields = profile.fields;
                searchResults.innerHTML += `
                <div class="cart">
                <a href="/profile/${fields.username}"><div>
                    <div class="img">
                        <img src="/media/${fields.avatar}" alt="Profile">
                    </div>
                    <div class="info">
                        <p class="name">${fields.username}</p>
                        <p class="second_name">${fields.displayname}</p>
                    </div>
                </div></a>
                </div>
                `;
            });
        } else {
            searchResults.innerHTML = `
            <div class="cart">
              <div>
                  <p class="name">No results found</p>
              </div>
            </div>
            `;
        }
    });
  });
});

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function clearSearchResults() {
  const searchResults = document.getElementById('searchResults');
  searchResults.innerHTML = '';
}

function followOrUnfollow(username, action, page) {
    console.log(username, action);
    fetch("/follow/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            username: username,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (action === "follow") {
            if (page === "profile") {
                const followButton = document.getElementById("follow__profile__id");
                followButton.style.display = "none";
                const unfollowButton = document.getElementById("unfollow__profile__id");
                unfollowButton.style.display = "block";
                const followersCount = document.getElementById("followers__count");
                followersCount.innerHTML = parseInt(followersCount.innerHTML) + 1;
            }
            else {
                const followButton = document.getElementById(`followbtn-${username}`);
                followButton.style.display = "none";
                const unfollowButton = document.getElementById(`unfollowbtn-${username}`);
                unfollowButton.style.display = "block";
            }
            
        }
        else if (action === "unfollow") {
            if (page === "profile") {
                const followButton = document.getElementById("follow__profile__id");
                followButton.style.display = "block";
                const unfollowButton = document.getElementById("unfollow__profile__id");
                unfollowButton.style.display = "none";
                const followersCount = document.getElementById("followers__count");
                followersCount.innerHTML = parseInt(followersCount.innerHTML) - 1;
            }
            else {
                const followButton = document.getElementById(`followbtn-${username}`);
                followButton.style.display = "block";
                const unfollowButton = document.getElementById(`unfollowbtn-${username}`);
                unfollowButton.style.display = "none";
            }
        }
    });
}

function sendMessage(id, action) {
    var message = "";
    console.log(id);
    console.log(action);
    if (action == 'notinmodal')
        message = document.getElementById(`not_inpost_message_${id}`).value;
    else    
        message = document.getElementById(`post_message_${id}`).value;
    fetch("/send_message_post/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            id: id,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "ok") {
            
            const messageSent = document.getElementById(`messageListField-${id}`);
            const avatarUrl = data.comment.avatar_url || 'static/assets/profile-photos/default-photo.png';
            const username = data.comment.username || 'Unknown User';
            const commentText = data.comment.comment || '';        

            const commentHTML = `
                <div class="modal-post-comment">
                    <img src="${avatarUrl}" alt="Avatar" class="modal-post-comment-img">
                    <a href="/profile/${username}" class="modal-post-comment-username">${username}</a>
                    <p class="modal-post-comment-comment">${commentText}</p>
                </div>
            `;
            messageSent.innerHTML += commentHTML;
            document.getElementById(`post_message_${id}`).value = '';
            document.getElementById(`not_inpost_message_${id}`).value = '';
        }
    });
}