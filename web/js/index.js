const pages = ['dashboard', 'discover', 'recordings', 'store'];

pages.forEach(function (page) {
  document.querySelector(`.nav-link[data-link=${page}]`).addEventListener('click', function (event) {
    let selected = event.target.dataset.link;
    document.getElementById(selected).classList.remove('d-none');
    document.querySelectorAll(`.page:not(#${selected})`).forEach((page) => {page.classList.add('d-none');}) 
  });
});

class TmdbRequests {
  constructor() {
    this.baseUrl = 'https://api.themoviedb.org/3';
    this.imageBaseUrl = 'https://image.tmdb.org/t/p';
    this.apiKey = 'da4e2da40f03d372b95f5dbd4a92e6b8';
    this.language = 'de';
  }

  async getContents({ type = 'movie', searchTerm = null } = {}) {
    let path = searchTerm ? `/search/${type}` : `/trending/${type}/week`;
    let query = searchTerm ? `&query=${searchTerm}` : '';
    let res = await fetch(`${this.baseUrl}${path}?api_key=${this.apiKey}&language=${this.language}${query}`);
    if (res.ok) {
      let data = await res.json();
      return data.results;
    } else {
      return [];
    }
  }

  getPoster(path, size='w185') {
    if (path) {
      return `${this.imageBaseUrl}/${size}/${path}`;
    } else {
      return '';
    }
  }
}

let trendingMovies, trendingTv;

async function displayResults(searchTerm = null) {
  startLoadingAnimation('movie');
  startLoadingAnimation('tv');
  trendingMovies = await tmdbRequests.getContents({ searchTerm: searchTerm });
  trendingTv = await tmdbRequests.getContents({ type: 'tv', searchTerm: searchTerm });
  
  clearResults('movie');
  clearResults('tv');
  trendingMovies.forEach(function (movie) {
    /**
     * fill movie columns
     */
    addContentCard(movie);
  });
  trendingTv.forEach(function (series) {
    addContentCard(series, 'tv');
  });
  stopLoadingAnimation('movie');
  stopLoadingAnimation('tv');
}

const tmdbRequests = new TmdbRequests();

document.querySelector('.nav-link[data-link=discover]').addEventListener('click', async function() {
  displayResults();
});

document.getElementById('search-item').addEventListener('click', async function () {
  displayResults(document.getElementById('search-term').value);
});

document.getElementById('search-term').addEventListener('keydown', async function(e) {
  if (e.key == 'Enter') {
    displayResults(document.getElementById('search-term').value);
  }
})

async function addContentCard(data, type = 'movie') {
  let imagePath = type == 'movie' ? data.backdrop_path : data.poster_path;
  const imgSrc = tmdbRequests.getPoster(imagePath);
  const modalImgSrc = tmdbRequests.getPoster(imagePath, size='w500');
  const title = type == 'movie' ? data.title : data.name;
  const overview = `${data.overview}`;
  const overviewCropped = `${overview.substring(0, 80)}...`;
  const id = data.id;
  let content_date = type == 'movie' ? data.release_date : data.first_air_date;

  let owned = await eel.checkIfContentExists(id, type)();

  let movieContainer = document.createElement('div');
  movieContainer.classList.add('col-md-4', 'col-sm-6', 'mt-3');
  let movieCard = document.createElement('div');
  movieCard.classList.add('card');
  if (owned) {
    movieCard.classList.add('text-white', 'bg-dark');
  }
  movieCard.setAttribute('data-content-id', id);
  movieCard.role = 'button';
  movieCard.setAttribute('data-bs-toggle', 'modal');
  movieCard.setAttribute('data-bs-target', `#content-${id}`);
  let movieImage;
  if (imgSrc) {
    movieImage = document.createElement('img');
    movieImage.classList.add('card-img-top');
    movieImage.alt = title;
    movieImage.src = imgSrc;
  }
  let movieCardBody = document.createElement('div');
  movieCardBody.classList.add('card-body');
  let movieCardTitle = document.createElement('h5');
  movieCardTitle.classList.add('card-title');
  movieCardTitle.innerText = title;
  let movieCardOverview = document.createElement('p');
  movieCardOverview.innerText = overviewCropped;
  movieCardOverview.classList.add('card-text', 'small');
  // let movieCardButton = document.createElement('button');
  // movieCardButton.type = 'button';
  // movieCardButton.classList.add('btn', 'btn-outline-secondary');
  // movieCardButton.innerText = 'Hinzufügen';
  // movieCardButton.dataset.action = 'add';
  // movieCardButton.addEventListener('click', function () {
  //   switch (this.dataset.action) {
  //     case 'add':
  //       console.log('add ' + id);
  //       break;
  //     case 'edit':
  //       console.log('edit ' + id);
  //       break;
  //     default:
  //       break;
  //   }
  // });

  movieContainer.append(movieCard);
  if (imgSrc) {
    movieCard.append(movieImage);
  }
  movieCard.append(movieCardBody);
  movieCardBody.append(movieCardTitle);
  movieCardBody.append(movieCardOverview);
  // movieCardBody.append(movieCardButton);

  let movieModal = document.createElement('div');
  movieModal.classList.add('modal', 'fade');
  movieModal.setAttribute('id', `content-${id}`);
  movieModal.tabIndex = -1;
  movieModal.setAttribute('aria-labelledby', `content-${id}-title`);
  movieModal.setAttribute('aria-hidden', true);

  let movieModalDialog = document.createElement('div');
  movieModalDialog.classList.add('modal-dialog', 'modal-dialog-scrollable');
  let movieModalContent = document.createElement('div');
  movieModalContent.classList.add('modal-content');
  let movieModalHeader = document.createElement('div');
  movieModalHeader.classList.add('modal-header');
  let movieModalTitle = document.createElement('h5');
  movieModalTitle.classList.add('modal-title');
  movieModalTitle.setAttribute('id', `content-${id}-title`);
  movieModalTitle.innerText = title;
  let movieModalBody = document.createElement('div');
  movieModalBody.classList.add('modal-body');
  let movieModalImage;
  if (modalImgSrc) {
    movieModalImage = document.createElement('img');
    movieModalImage.alt = title;
    movieModalImage.src = modalImgSrc;
    movieModalImage.classList.add('w-100');
  }
  let movieModalOverview = document.createElement('p');
  movieModalOverview.setAttribute('id', `content-${id}-overview`);
  movieModalOverview.classList.add('small');
  movieModalOverview.innerText = overview;
  let movieModalOverviewLabel = document.createElement('label');
  movieModalOverviewLabel.classList.add('mt-3');
  movieModalOverviewLabel.setAttribute('for', `content-${id}-overview`);
  movieModalOverviewLabel.innerText = 'Beschreibung';
  let movieModalOverviewDivider = document.createElement('hr');
  let movieModalDate = document.createElement('p');
  movieModalDate.setAttribute('id', `content-${id}-date`);
  movieModalDate.classList.add('small');
  movieModalDate.innerText = content_date.split('-').reverse().join('.');
  let movieModalDateLabel = document.createElement('label');
  movieModalDateLabel.setAttribute('for', `content-${id}-date`);
  movieModalDateLabel.classList.add('mt-3');
  movieModalDateLabel.innerText = type == 'movie' ? 'Erscheinungsjahr' : 'Erstausstrahlungsjahr';
  let movieModalDateDivider = document.createElement('hr');
  let modalButton = document.createElement('button');
  modalButton.type = 'button';
  modalButton.classList.add('btn', 'btn-outline-secondary', 'content-action');
  modalButton.innerText = owned ? 'Entfernen' : 'Hinzufügen';
  modalButton.dataset.action = owned ? 'remove' : 'add';
  modalButton.addEventListener('click', function () {
    switch (this.dataset.action) {
      case 'add':
        switch (type) {
          case 'movie':
            eel.addMovie(data);
            break;
          case 'tv':
            eel.addSeriesByTmdbId(id);
            break;
          default:
            break;
        }
        
        console.log(data)
        this.dataset.action = 'remove';
        this.innerText = 'Entfernen';
        movieCard.classList.add('text-white', 'bg-dark');
        // console.log('add ' + id);
        break;
      case 'remove':
        console.log('remove ' + id);
        eel.removeContent(id);
        this.dataset.action = 'add';
        this.innerText = 'Hinzufügen';
        movieCard.classList.remove('text-white', 'bg-dark');
        break;
      default:
        break;
    }
  });

  movieContainer.append(movieModal);
  movieModal.append(movieModalDialog);
  movieModalDialog.append(movieModalContent);
  movieModalContent.append(movieModalHeader);
  movieModalHeader.append(movieModalTitle);
  movieModalHeader.append(modalButton);
  movieModalContent.append(movieModalBody);
  if (modalImgSrc) {
    movieModalBody.append(movieModalImage);
  }
  movieModalBody.append(movieModalOverviewLabel);
  movieModalBody.append(movieModalOverviewDivider);
  movieModalBody.append(movieModalOverview);
  movieModalBody.append(movieModalDateLabel);
  movieModalBody.append(movieModalDateDivider);
  movieModalBody.append(movieModalDate);

  document.querySelector(`div.${type}`).append(movieContainer);
}

function startLoadingAnimation(target) {
  document.querySelector(`div.${target}-loading`).classList.remove('d-none');
  document.querySelector(`div.${target}`).classList.add('d-none');
}

function stopLoadingAnimation(target) {
  document.querySelector(`div.${target}-loading`).classList.add('d-none');
  document.querySelector(`div.${target}`).classList.remove('d-none');
}

function clearResults(target) {
  document.querySelector(`div.${target}`).innerHTML = '';
}