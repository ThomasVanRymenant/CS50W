currentPageLinkName = document.getElementById('pageLink')
// execute the following script if a pageLink was found (if we placed one in the template to be found)
if (currentPageLinkName != null) {

  // get reference to all nav-links
  var navLinks = document.getElementById('navbar').querySelectorAll('.nav-link');
  navLinksAmount = navLinks.length;

  // give the appropriate nav-link a class 'active', and remove a class 'active' from other nav-links if neccesary
  for (let i = 0; i < navLinksAmount; i++) {
    if (navLinks[i].textContent.toLowerCase() == currentPageLinkName.textContent.toLowerCase()) {
      if (navLinks[i].classList.contains('active') == false) {
        navLinks[i].classList.add('active');
      }
      break;
    } else {
      if (navLinks[i].classList.contains('active')) {
        navLinks[i].classList.remove('active');
      }
    }
  }
}