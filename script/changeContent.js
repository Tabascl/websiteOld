function toggleSite(target) {
    var toShow = document.getElementById(target);
    var divs = document.getElementsByClassName("dyntext")

    for (var i = 0; i<divs.length;i++) {
        divs[i].style.opacity = 0;
        divs[i].style.display = "none";
    }

    toShow.style.opacity = 1;
    toShow.style.display = 'block';
}