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

function followOrUnfollow(username, action) {
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
            const followButton = document.getElementById(`followbtn-${username}`);
            followButton.style.display = "none";
            const unfollowButton = document.getElementById(`unfollowbtn-${username}`);
            unfollowButton.style.display = "block";
        }
        else if (action === "unfollow") {
            const followButton = document.getElementById(`followbtn-${username}`);
            followButton.style.display = "block";
            const unfollowButton = document.getElementById(`unfollowbtn-${username}`);
            unfollowButton.style.display = "none";
        }
    });
}