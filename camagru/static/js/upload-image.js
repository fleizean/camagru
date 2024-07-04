let selectedEffect = "none";

function messageDisplay(display, message) {
    const msg = document.getElementById("msg");
    const msgText = document.getElementById("msgText");
  
    if (display) {
      msg.style.display = "block";
      msgText.textContent = message;
    } else {
      msg.style.display = "none";
    }
  }
  
  function captureDisplay(display) {
    const captureVideo = document.getElementById("captureVideo");
    const captureFilter = document.getElementById("captureFilter");
  
    if (display) {
      captureVideo.style.display = "block";
      captureFilter.style.display = "block";
    } else {
      captureVideo.style.display = "none";
      captureFilter.style.display = "none";
    }
  }
  
  function previewDisplay(display) {
    const canvasPreview = document.getElementById("photoPreview");
    const importPreview = document.getElementById("importPreview");
    const previewFilter = document.getElementById("previewFilter");
  
    if (display) {
      canvasPreview.style.display = "block";
      previewFilter.style.display = "block";
    } else {
      canvasPreview.style.display = "none";
      importPreview.style.display = "none";
      importPreview.src = "";
      previewFilter.style.display = "none";
    }
  }
  
  function importPreviewDisplay(uploadedImageData) {
    const importPreview = document.getElementById("importPreview");
    const previewFilter = document.getElementById("previewFilter");
  
    importPreview.style.display = "block";
    importPreview.src = uploadedImageData;
    previewFilter.style.display = "block";
  }
  
  function filtersDisplay(display) {
    const filters = document.getElementById("filters");
    
    if (display) {
      filters.style.display = "flex";
    } else {
      filters.style.display = "none";
    }
  }
  
  function waitingDisplay(display) {
    const waiting = document.getElementById("waiting");
  
    if (display) {
      waiting.style.display = "flex";
    } else {
      waiting.style.display = "none";
    }
  }
  
  function captureBtnDisplay(display) {
    const takePhotoBtn = document.getElementById("takePhotoBtn");
    const importBtn = document.getElementById("importBtn");
  
    if (display) {
      takePhotoBtn.style.display = "inline-block";
      importBtn.style.display = "inline-block";
    } else {
      takePhotoBtn.style.display = "none";
      importBtn.style.display = "none";
    }
  }
  
  function previewBtnDisplay(display) {
    const cancelBtn = document.getElementById("cancelBtn");
    const saveBtn = document.getElementById("saveBtn");
  
    if (display) {
      saveBtn.style.display = "inline-block";
      cancelBtn.style.display = "inline-block";
    } else {
      cancelBtn.style.display = "none";
      saveBtn.style.display = "none";
    }
  }

  function resetFilter() {
    const firstBtn = document.querySelector(".filterBtn[data-id='1']");
    firstBtn.click();
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const captureVideo = document.getElementById("captureVideo");
    const captureFilter = document.getElementById("captureFilter");
    const canvasPreview = document.getElementById("photoPreview");
    const previewFilter = document.getElementById("previewFilter");
    const filterBtns = document.querySelectorAll(".filterBtn");
    const takePhotoBtn = document.getElementById("takePhotoBtn");
    const importInput = document.getElementById("importInput");
    const cancelBtn = document.getElementById("cancelBtn");
    const descriptionContain = document.getElementById("descriptionContain");
    const saveBtn = document.getElementById("saveBtn");
    let selectedFilter = "1";
    let uploadedImageData = null;

    const startWebcam = async () => {
        const constraints = {
            audio: false,
            video: { width: 468, height: 585, facingMode: "user" },
        };
    
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            captureVideo.srcObject = stream;
        } catch (error) {
            messageDisplay(true, "Error accessing webcam: " + error);
        }
    };

    const stopWebcam = () => {
        const stream = captureVideo.srcObject;
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach((track) => track.stop());
            captureVideo.srcObject = null;
        }
    };

    const importFile = (e) => {
        const uploadedImage = e.target.files[0];
        if (uploadedImage) {
            const reader = new FileReader();
            reader.onload = () => {
                uploadedImageData = reader.result;
                importPreviewDisplay(uploadedImageData);
                captureDisplay(false);
                stopWebcam();
                resetFilter();
                waitingDisplay(false);
                descriptionContain.style.display = "block";
                captureBtnDisplay(false);
                previewBtnDisplay(true);
            };
            reader.readAsDataURL(uploadedImage);
        }
        e.currentTarget.value = null;
    };

    const filterBtnClick = (btn) => {
        const filter = "static/" + "assets/filters/" + btn.getAttribute("data-file");
        captureFilter.style.display = "block";
        captureFilter.src = filter;
        previewFilter.src = filter;
        takePhotoBtn.disabled = false;
        filterBtns.forEach((btn) => {
            btn.classList.remove("selected");
            btn.style.background = "transparent";
        });
        btn.classList.add("selected");
        btn.style.background = "#dbdbdb";
        selectedFilter = btn.getAttribute("data-file");
    };

    const takePhotoBtnClick = () => {
        canvasPreview.width = captureVideo.videoWidth;
        canvasPreview.height = captureVideo.videoHeight;
        canvasPreview
            .getContext("2d")
            .drawImage(captureVideo, 0, 0, canvasPreview.width, canvasPreview.height);
    
        captureDisplay(false);
        previewDisplay(true);
        filtersDisplay(false);
        waitingDisplay(false);
        captureBtnDisplay(false);
        previewBtnDisplay(true);
        descriptionContain.style.display = "block";
    };

    const cancelBtnClick = async () => {
        messageDisplay(false, null);
        startWebcam();
        captureDisplay(true);
        previewDisplay(false);
        uploadedImageData = null;
        resetFilter();
        filtersDisplay(true);
        captureBtnDisplay(true);
        previewBtnDisplay(false);
    };

    const saveBtnClick = async () => {
        const image = uploadedImageData || canvasPreview.toDataURL("image/jpeg");
        const description = document.getElementById("description").value;
        const effect = selectedEffect;
        const req = await savePhotoApi(image, selectedFilter, description, effect);
        if (!req.success) {
            messageDisplay(true, req.message);
        }
    };

    startWebcam();
    importInput.addEventListener("change", (e) => importFile(e));
    filterBtns.forEach((btn) => {
        btn.addEventListener("click", () => filterBtnClick(btn));
    });
    takePhotoBtn.addEventListener("click", takePhotoBtnClick);
    cancelBtn.addEventListener("click", cancelBtnClick);
    saveBtn.addEventListener("click", saveBtnClick);

});

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

function savePhotoApi(image, filter, description, effect) {
    console.log(filter);
    console.log(effect);
    console.log(image);
    return fetch("/save-photo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ image, filter, description, effect}),
    }).then((res) => res.json());
}


function applyFilter(filter) {
  const captureFilter = document.getElementById("captureFilter");
  const previewFilter = document.getElementById("importPreview");
  const photoPreview = document.getElementById("photoPreview");
  selectedEffect = filter;

  captureFilter.style.filter = filter;
  previewFilter.style.filter = filter;
  photoPreview.style.filter = filter;
}

function deletePost(id) {
  Swal.fire({
    title: 'Are you sure?',
    text: "You won't be able to revert this!",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!'
  }).then((result) => {
    if (result.isConfirmed) {
      fetch("/delete-post", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ id }),
      })
      .then((res) => res.json())
      .then((data) => {
        if (data.status == "ok") {
          const deletedPost = document.getElementById(`deletedPost-${id}`);
          deletedPost.style.display = "none";
          Swal.fire(
            'Deleted!',
            'Your post has been deleted.',
            'success'
          )
        }
      });
    }
  })
}