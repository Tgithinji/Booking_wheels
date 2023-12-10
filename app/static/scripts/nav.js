const nav = document.querySelector('.primary-nav');
const toggle = document.querySelector('.nav-toggle');

toggle.addEventListener('click', () => {
	const visible = nav.getAttribute('data-visible');

	if (visible === 'false') {
		nav.setAttribute('data-visible', true);
		toggle.setAttribute('aria-expanded', true);
		toggle.innerHTML = '<i class="fa-solid fa-xmark"></i>';
	} else if (visible === 'true') {
		nav.setAttribute('data-visible', false);
		toggle.setAttribute('aria-expanded', false);
		toggle.innerHTML = '<i class="fa-solid fa-bars"></i>';
	}
});
