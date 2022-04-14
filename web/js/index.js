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
  const overviewCropped = overview.length > 80 ? `${overview.substring(0, 80)}...` : overview;
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
        // console.log('add ' + id);
  //       break;
  //     case 'edit':
        // console.log('edit ' + id);
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

  let seasonsLabel, seasonsDivider, seasonsRow;
  if (type == 'tv') {
    seasonsLabel = document.createElement('label');
    seasonsLabel.setAttribute('for', `tv-${id}-seasons`);
    seasonsLabel.innerText = 'Staffeln';  
    seasonsLabel.classList.add('mt-3');
    seasonsDivider = document.createElement('hr');
    seasonsRow = document.createElement('div');
    seasonsRow.setAttribute('id', `tv-${id}-seasons`);
    seasonsRow.classList.add('row');
    let seasons = await eel.getSeasonsById(id)();
    seasons.forEach(async function (season) {
      let seasonContainer = document.createElement('div');
      seasonContainer.classList.add('col-md-6', 'col-sm-6', 'mt-3');
      let seasonCard = document.createElement('div');
      seasonCard.classList.add('card');
      let seasonOwned = await eel.checkIfSeasonExists(id, season.season_number)();
      if (seasonOwned) {
        seasonCard.classList.add('text-white', 'bg-dark');
      }
      seasonCard.role = 'button';
      seasonCard.setAttribute('data-bs-toggle', 'modal');
      seasonCard.setAttribute('data-bs-target', `#content-${id}-season-${season.season_number}`);
      let seasonImage;
      let seasonImageSrc = tmdbRequests.getPoster(season.poster_path, 'w500');
      if (seasonImageSrc) {
        seasonImage = document.createElement('img');
        seasonImage.classList.add('card-img-top');
        seasonImage.alt = title + ': ' + season.name;
        seasonImage.src = seasonImageSrc;
      }
      let seasonOverview = season.overview;
      let seasonOverviewCropped = seasonOverview.length > 80 ? `${seasonOverview.substring(0, 80)}...` : seasonOverview;
      let seasonCardBody = document.createElement('div');
      seasonCardBody.classList.add('card-body');
      let seasonCardTitle = document.createElement('h5');
      seasonCardTitle.classList.add('card-title');
      seasonCardTitle.innerText = season.name;
      let seasonCardOverview = document.createElement('p');
      seasonCardOverview.innerText = seasonOverviewCropped;
      seasonCardOverview.classList.add('card-text', 'small');

      seasonContainer.append(seasonCard);
      if (seasonImageSrc) {
        seasonCard.append(seasonImage);
      }
      seasonCard.append(seasonCardBody);
      seasonCardBody.append(seasonCardTitle);
      seasonCardBody.append(seasonCardOverview);
      seasonsRow.append(seasonContainer);

      let seasonModal = document.createElement('div');
      seasonModal.classList.add('modal', 'fade');
      seasonModal.setAttribute('id', `content-${id}-season-${season.season_number}`);
      seasonModal.tabIndex = -1;
      seasonModal.setAttribute('aria-labelledby', `content-${id}-season-${season.season_number}-title`);
      seasonModal.setAttribute('aria-hidden', true);

      let seasonModalDialog = document.createElement('div');
      seasonModalDialog.classList.add('modal-dialog', 'modal-dialog-scrollable');
      let seasonModalContent = document.createElement('div');
      seasonModalContent.classList.add('modal-content');
      let seasonModalHeader = document.createElement('div');
      seasonModalHeader.classList.add('modal-header');
      let seasonModalTitle = document.createElement('h5');
      seasonModalTitle.classList.add('modal-title');
      seasonModalTitle.setAttribute('id', `content-${id}-season-${season.season_number}-title`);
      seasonModalTitle.innerText = season.name;
      let seasonModalBody = document.createElement('div');
      seasonModalBody.classList.add('modal-body');
      let seasonModalImage;
      if (seasonImageSrc) {
        seasonModalImage = document.createElement('img');
        seasonModalImage.alt = `${title}: ${season.name}`;
        seasonModalImage.src = seasonImageSrc;
        seasonModalImage.classList.add('w-100');
      }
      let seasonModalOverview = document.createElement('p');
      seasonModalOverview.setAttribute('id', `content-${id}-season-${season.season_number}-overview`);
      seasonModalOverview.classList.add('small');
      seasonModalOverview.innerText = seasonOverview;
      let seasonModalOverviewLabel = document.createElement('label');
      seasonModalOverviewLabel.classList.add('mt-3');
      seasonModalOverviewLabel.setAttribute('for', `content-${id}-season-${season.season_number}-overview`);
      seasonModalOverviewLabel.innerText = 'Beschreibung';
      let seasonModalOverviewDivider = document.createElement('hr');
      let seasonModalDate = document.createElement('p');
      seasonModalDate.setAttribute('id', `content-${id}-season-${season.season_number}-date`);
      seasonModalDate.classList.add('small');
      let seasonDate = season.air_date ? season.air_date : '';
      seasonModalDate.innerText = seasonDate.split('-').reverse().join('.');
      let seasonModalDateLabel = document.createElement('label');
      seasonModalDateLabel.setAttribute('for', `content-${id}-season-${season.season_number}-date`);
      seasonModalDateLabel.classList.add('mt-3');
      seasonModalDateLabel.innerText = 'Erstausstrahlungsjahr';
      let seasonModalDateDivider = document.createElement('hr');

      let episodes = await eel.getEpisodesByIdAndNumber(id, season.season_number)();
      let episodesLabel = document.createElement('label');
      episodesLabel.setAttribute('for', `tv-${id}-season-${season.season_number}-episodes`);
      episodesLabel.innerText = 'Episoden';  
      episodesLabel.classList.add('mt-3');
      episodesDivider = document.createElement('hr');
      let episodesRow = document.createElement('div');
      episodesRow.setAttribute('id', `tv-${id}-season-${season.season_number}-episodes`);
      episodesRow.classList.add('row');
      episodes.forEach(async function (episode) {
        let episodeContainer = document.createElement('div');
        episodeContainer.classList.add('col-md-6', 'col-sm-6', 'mt-3');
        let episodeCard = document.createElement('div');
        episodeCard.classList.add('card');
        let episodeOwned = await eel.checkIfEpisodeExists(id, season.season_number, episode.episode_number)();
        if (episodeOwned) {
          episodeCard.classList.add('text-white', 'bg-dark');
        }
        episodeCard.role = 'button';
        episodeCard.setAttribute('data-bs-toggle', 'modal');
        episodeCard.setAttribute('data-bs-target', `#content-${id}-season-${season.season_number}-episode-${episode.episode_number}`);
        let episodeImage;
        let episodeImageSrc = tmdbRequests.getPoster(episode.still_path);
        if (episodeImageSrc) {
          episodeImage = document.createElement('img');
          episodeImage.classList.add('card-img-top');
          episodeImage.alt = season.name + ': ' + episode.name
          episodeImage.src = episodeImageSrc;
        }
        let episodeOverview = episode.overview;
        let episodeOverviewCropped = episodeOverview.length > 80 ? `${episodeOverview.substring(0, 80)}...` : episodeOverview;
        let episodeCardBody = document.createElement('div');
        episodeCardBody.classList.add('card-body');
        let episodeCardTitle = document.createElement('h5');
        episodeCardTitle.classList.add('card-title');
        episodeCardTitle.innerText = episode.name;
        let episodeCardOverview = document.createElement('p');
        episodeCardOverview.innerText = episodeOverviewCropped;
        episodeCardOverview.classList.add('card-text', 'small');

        episodeContainer.append(episodeCard);
        if (episodeImageSrc) {
          episodeCard.append(episodeImage);
        }
        episodeCard.append(episodeCardBody);
        episodeCardBody.append(episodeCardTitle);
        episodeCardBody.append(episodeCardOverview);
        episodesRow.append(episodeContainer);

        let episodeModal = document.createElement('div');
        episodeModal.classList.add('modal', 'fade');
        episodeModal.setAttribute('id', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}`);
        episodeModal.tabIndex = -1;
        episodeModal.setAttribute('aria-labelledby', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-title`);
        episodeModal.setAttribute('aria-hidden', true);

        let episodeModalDialog = document.createElement('div');
        episodeModalDialog.classList.add('modal-dialog', 'modal-dialog-scrollable');
        let episodeModalContent = document.createElement('div');
        episodeModalContent.classList.add('modal-content');
        let episodeModalHeader = document.createElement('div');
        episodeModalHeader.classList.add('modal-header');
        let episodeModalTitle = document.createElement('h5');
        episodeModalTitle.classList.add('modal-title');
        episodeModalTitle.setAttribute('id', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-title`);
        episodeModalTitle.innerText = episode.name;
        let episodeModalBody = document.createElement('div');
        episodeModalBody.classList.add('modal-body');
        let episodeModalImage;
        let episodeModalImageSrc = tmdbRequests.getPoster(episode.still_path, 'w500');
        if (episodeModalImageSrc) {
          episodeModalImage = document.createElement('img');
          episodeModalImage.alt = `${season.name}: ${episode.name}`;
          episodeModalImage.src = episodeModalImageSrc;
          episodeModalImage.classList.add('w-100');
        }
        let episodeModalOverview = document.createElement('p');
        episodeModalOverview.setAttribute('id', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-overview`);
        episodeModalOverview.classList.add('small');
        episodeModalOverview.innerText = episodeOverview;
        let episodeModalOverviewLabel = document.createElement('label');
        episodeModalOverviewLabel.classList.add('mt-3');
        episodeModalOverviewLabel.setAttribute('for', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-overview`);
        episodeModalOverviewLabel.innerText = 'Beschreibung';
        let episodeModalOverviewDivider = document.createElement('hr');
        let episodeModalDate = document.createElement('p');
        episodeModalDate.setAttribute('id', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-date`);
        episodeModalDate.classList.add('small');
        let episodeDate = episode.air_date ? episode.air_date : '';
        episodeModalDate.innerText = episodeDate.split('-').reverse().join('.');
        let episodeModalDateLabel = document.createElement('label');
        episodeModalDateLabel.setAttribute('for', `content-${id}-season-${season.season_number}-episode-${episode.episode_number}-date`);
        episodeModalDateLabel.classList.add('mt-3');
        episodeModalDateLabel.innerText = 'Ausstrahlungsjahr';
        let episodeModalDateDivider = document.createElement('hr');

        let episodeBackButton = document.createElement('button');
        episodeBackButton.classList.add('btn', 'btn-outline-secondary', 'episode-back');
        let episodeTitleCropped = season.name > 17 ? season.name.substring(0, 17) : season.name;
        episodeBackButton.innerText = 'Zurück zu ' + episodeTitleCropped;
        episodeBackButton.setAttribute('data-bs-toggle', 'modal');
        episodeBackButton.setAttribute('data-bs-target', `#content-${id}-season-${season.season_number}`);
        let episodeButton = document.createElement('button');
        episodeButton.classList.add('btn', 'btn-outline-secondary', 'episode-action');
        episodeButton.innerText = episodeOwned ? 'Entfernen' : 'Hinzufügen';
        episodeButton.dataset.action = episodeOwned ? 'remove' : 'add';
        episodeButton.addEventListener('click', async function () {
          switch (this.dataset.action) {
            case 'add':
              eel.addEpisodeByTmdbIdAndNumber(id, season.season_number, episode.episode_number);
              await displayRecordings();
              await fillAddRecordingForm();
              this.dataset.action = 'remove';
              this.innerText = 'Entfernen';
              episodeCard.classList.add('text-white', 'bg-dark');
              break;
            case 'remove':
              eel.removeEpisodeByIdAndNumber(id, season.season_number, episode.episode_number);
              await displayRecordings();
              await fillAddRecordingForm();
              this.dataset.action = 'add';
              this.innerText = 'Hinzufügen';
              episodeCard.classList.remove('text-white', 'bg-dark');
              break;
            default:
              break;
          }
        });

        episodeModal.append(episodeModalDialog);
        episodeModalDialog.append(episodeModalContent);
        episodeModalContent.append(episodeModalHeader);
        episodeModalHeader.append(episodeModalTitle);
        episodeModalHeader.append(episodeBackButton);
        episodeModalHeader.append(episodeButton);
        episodeModalContent.append(episodeModalBody);
        if (episodeImageSrc) {
          episodeModalBody.append(episodeModalImage);
        }
        episodeModalBody.append();
        episodeModalBody.append(episodeModalOverviewDivider);
        episodeModalBody.append(episodeModalOverview);
        episodeModalBody.append(episodeModalDateLabel);
        episodeModalBody.append(episodeModalDateDivider);
        episodeModalBody.append(episodeModalDate);

        movieContainer.append(episodeModal);
      });

      let seasonBackButton = document.createElement('button');
      seasonBackButton.classList.add('btn', 'btn-outline-secondary', 'season-back');
      let seasonTitleCropped = title.length > 17 ? title.substring(0, 17) + '...' : title;
      seasonBackButton.innerText = 'Zurück zu ' + seasonTitleCropped;
      seasonBackButton.setAttribute('data-bs-toggle', 'modal');
      seasonBackButton.setAttribute('data-bs-target', `#content-${id}`);
      let seasonButton = document.createElement('button');
      seasonButton.type = 'button';
      seasonButton.classList.add('btn', 'btn-outline-secondary', 'season-action');
      seasonButton.innerText = seasonOwned ? 'Entfernen' : 'Hinzufügen';
      seasonButton.dataset.action = seasonOwned ? 'remove' : 'add';
      seasonButton.addEventListener('click', async function () {
        switch (this.dataset.action) {
          case 'add':
            eel.addSeasonByTmdbIdAndNumber(id, season.season_number);
            await displayRecordings();
            await fillAddRecordingForm();
            this.dataset.action = 'remove';
            this.innerText = 'Entfernen';
            seasonCard.classList.add('text-white', 'bg-dark');
            break;
          case 'remove':
            eel.removeSeasonByIdAndNumber(id, season.season_number);
            await displayRecordings();
            await fillAddRecordingForm();
            this.dataset.action = 'add';
            this.innerText = 'Hinzufügen';
            seasonCard.classList.remove('text-white', 'bg-dark');
            break;
          default:
            break;
        }
      });

      seasonModal.append(seasonModalDialog);
      seasonModalDialog.append(seasonModalContent);
      seasonModalContent.append(seasonModalHeader);
      seasonModalHeader.append(seasonModalTitle);
      seasonModalHeader.append(seasonBackButton);
      seasonModalHeader.append(seasonButton);
      seasonModalContent.append(seasonModalBody);
      if (seasonImageSrc) {
        seasonModalBody.append(seasonModalImage);
      }
      seasonModalBody.append(seasonModalOverviewLabel);
      seasonModalBody.append(seasonModalOverviewDivider);
      seasonModalBody.append(seasonModalOverview);
      seasonModalBody.append(seasonModalDateLabel);
      seasonModalBody.append(seasonModalDateDivider);
      seasonModalBody.append(seasonModalDate);
      seasonModalBody.append(episodesLabel);
      seasonModalBody.append(episodesDivider);
      seasonModalBody.append(episodesRow);

      movieContainer.append(seasonModal); 
    });
  }

  let modalButton = document.createElement('button');
  modalButton.type = 'button';
  modalButton.classList.add('btn', 'btn-outline-secondary', 'content-action');
  modalButton.innerText = owned ? 'Entfernen' : 'Hinzufügen';
  modalButton.dataset.action = owned ? 'remove' : 'add';
  modalButton.addEventListener('click', async function () {
    switch (this.dataset.action) {
      case 'add':
        switch (type) {
          case 'movie':
            eel.addMovie(data);
            await displayRecordings();
            await fillAddRecordingForm();
            break;
          case 'tv':
            eel.addSeriesByTmdbId(id);
            await displayRecordings();
            await fillAddRecordingForm();
            break;
          default:
            break;
        }
        
        // console.log(data)
        this.dataset.action = 'remove';
        this.innerText = 'Entfernen';
        movieCard.classList.add('text-white', 'bg-dark');
        // console.log('add ' + id);
        break;
      case 'remove':
        // console.log('remove ' + id);
        eel.removeContent(id);
        await displayRecordings();
        await fillAddRecordingForm();
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
  if (type == 'tv') {
    movieModalBody.append(seasonsLabel);
    movieModalBody.append(seasonsDivider);
    movieModalBody.append(seasonsRow);
  }

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

async function printLocations(id, parent = '') {
  let locations = await eel.getLocationsByParentId(id)();
  locations.forEach(function (location) {
    // console.log(lo// // cation[0])
    // console.log(parent + lo// // cation[1] + ': ' + lo// // cation[2]);
    printLocations(location[0], location[1] + ' > ');
  });
}

document.querySelector('.nav-link[data-link=store]').addEventListener('click', async function() {
  document.getElementById('store').innerHTML = '';
  displayLocations(null);
});

async function displayLocations(parentId, curLocCollapse = null) {
  let locations = await eel.getLocationsByParentId(parentId)();
  let parentLocationId = parentId ? parentId : 0;
  let parentLocAcc = document.createElement('div');
  parentLocAcc.id = `acc-loc-${parentLocationId}`;
  if (parentId == null) {
    parentLocAcc.classList.add('mt-3');
  }
  if (curLocCollapse == null) {
    document.getElementById('store').append(parentLocAcc);
  } else {
    curLocCollapse.querySelector('.card-body').append(parentLocAcc);
  }
  locations.forEach(async function (location) {
    let currentLocationId = location[0];
    let currentLocationName = location[1];
    let currentLocationDesc = location[2];
    let colLocCurId = `collapse-loc-${currentLocationId}`;
    let heaLocCurId = `heading-loc-${currentLocationId}`;

    let currentLocCard = document.createElement('div');
    currentLocCard.classList.add('card');
    let currentLocCardHeader = document.createElement('div');
    currentLocCardHeader.classList.add('card-header', 'd-flex', 'justify-content-between', 'align-items-center');
    currentLocCardHeader.id = heaLocCurId;
    let currentLocHeading = document.createElement('h5');
    currentLocHeading.classList.add('mb-0');
    let currentLocationLink = document.createElement('a');
    currentLocationLink.classList.add('nav-link');
    currentLocationLink.role = 'button';
    currentLocationLink.setAttribute('data-bs-toggle', 'collapse');
    currentLocationLink.href = `#${colLocCurId}`;
    currentLocationLink.ariaExpanded = false;
    currentLocationLink.setAttribute('aria-controls', colLocCurId);
    currentLocationLink.innerHTML = currentLocationName;
    let currentLocationCollapse = document.createElement('div');
    currentLocationCollapse.classList.add('collapse');
    if (localStorage.getItem(`open-collapse-${colLocCurId}`)) {
      currentLocationCollapse.classList.add('show');
    }
    currentLocationCollapse.id = colLocCurId;
    currentLocationCollapse.setAttribute('aria-labelledby', heaLocCurId);
    let currentLocCardBody = document.createElement('div');
    currentLocCardBody.classList.add('card-body');
    let currentLocCardText = document.createElement('p');
    currentLocCardText.classList.add('card-text');
    currentLocCardText.innerHTML = currentLocationDesc;
    let currentLocDeleteButton = document.createElement('button');
    currentLocDeleteButton.classList.add('btn', 'btn-danger');
    currentLocDeleteButton.innerText = 'Entfernen';
    currentLocDeleteButton.addEventListener('click', function () {
      eel.removeLocationById(currentLocationId);
      localStorage.removeItem(`open-collapse-${colLocCurId}`);
      document.getElementById('store').innerHTML = '';
      displayLocations(null);
    });

    currentLocationCollapse.addEventListener('shown.bs.collapse', function () {
      localStorage.setItem(`open-collapse-${colLocCurId}`, true);
    });
    currentLocationCollapse.addEventListener('hidden.bs.collapse', function () {
      localStorage.removeItem(`open-collapse-${colLocCurId}`);
    })

    parentLocAcc.append(currentLocCard);
    currentLocCard.append(currentLocCardHeader);
    currentLocCardHeader.append(currentLocHeading);
    currentLocCardHeader.append(currentLocDeleteButton);
    currentLocHeading.append(currentLocationLink);
    currentLocCard.append(currentLocationCollapse);
    currentLocationCollapse.append(currentLocCardBody);
    currentLocCardBody.append(currentLocCardText);

    await displayLocations(currentLocationId, currentLocationCollapse);
    await displayAddLocationForm(currentLocCardBody, currentLocationId);
  });
  if (!parentId) {
    await displayAddLocationForm(parentLocAcc, parentLocationId);
  }
}

async function displayAddLocationForm(target, parentLocationId) {
  let addLocationForm = document.createElement('form');
  let locationNameGroup = document.createElement('div');
  locationNameGroup.classList.add('input-group');
  let locationNameLabel = document.createElement('span');
  locationNameLabel.classList.add('input-group-text');
  locationNameLabel.innerText = 'Bezeichnung';
  let locationNameInput = document.createElement('input');
  locationNameInput.type = 'text';
  locationNameInput.classList.add('form-control');
  let locationDescGroup = document.createElement('div');
  locationDescGroup.classList.add('input-group');
  let locationDescLabel = document.createElement('span');
  locationDescLabel.classList.add('input-group-text');
  locationDescLabel.innerText = 'Beschreibung';
  let locationDescInput = document.createElement('textarea');
  locationDescInput.classList.add('form-control');
  let addLocationButton = document.createElement('button');
  addLocationButton.classList.add('btn', 'btn-secondary');
  addLocationButton.innerText = 'Hinzufügen';
  addLocationButton.addEventListener('click', async function (e) {
    e.preventDefault();
    let locationName = locationNameInput.value;
    if (locationName.length == 0) return;
    let locationDesc = locationDescInput.value;
    await eel.addLocation(parentLocationId, locationName, locationDesc);
    document.getElementById('store').innerHTML = '';
    displayLocations(null);
    await fillAddRecordingForm();
  });

  addLocationForm.append(locationNameGroup);
  addLocationForm.append(locationDescGroup);
  addLocationForm.append(addLocationButton);
  locationNameGroup.append(locationNameLabel);
  locationNameGroup.append(locationNameInput);
  locationDescGroup.append(locationDescLabel);
  locationDescGroup.append(locationDescInput);

  target.append(addLocationForm);
}

async function addContentsStorement(tmdbId, isMovie, locationId, amount = 1, recordingDate = null, notes = '') {
  await eel.addContentsStorement(tmdbId, isMovie, locationId, amount, recordingDate, notes);
}

async function addSeasonsStorement(tmdbId, seasonNumber, locationId, amount = 1, recordingDate = null, notes = '') {
  await eel.addSeasonsStorement(tmdbId, seasonNumber, locationId, amount, recordingDate, notes);
}

async function addEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, amount = 1, recordingDate = null, notes = '') {
  await eel.addEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, amount, recordingDate, notes);
}

async function fillAddRecordingForm() {
  let possessions = await eel.getPossessions()();
  // console.log(possessions)
  let fullLocations = await eel.getFullLocations()();
  // console.log(possessions, fullLo// cations);
  let recordingSelect = document.getElementById('recording');
  recordingSelect.innerHTML = '';
  let locationSelect = document.getElementById('location');
  locationSelect.innerHTML = '';
  let addRecordingButton = document.getElementById('add-recording');
  let amountInput = document.getElementById('amount');
  let recordingDateInput = document.getElementById('recording-date');
  let notesInput = document.getElementById('notes');
  possessions.forEach(async function (possession, index) {
    // console.log(possession)
    let option = document.createElement('option');
    // console.log(possession)
    // let fullTitle = await eel.getFullTitle(possession[0], possession[2], possession[3])();
    // option.innerText = fullTitle;
    option.innerText = possession[4];
    option.value = index;
    recordingSelect.append(option);
  });
  fullLocations.forEach(function (fullLocation, index) {
    let option = document.createElement('option');
    option.innerText = fullLocation[1];
    option.value = index;
    locationSelect.append(option);
  });
  addRecordingButton.addEventListener('click', async function () {
    eel.addRecording(possessions[recordingSelect.value].slice(0, 4), fullLocations[locationSelect.value][0], amountInput.value, recordingDateInput.value, notesInput.value);
    await displayRecordings();
  });
}

async function displayRecordings() {
  let locations = await eel.getFullLocations()();
  let recordings = await eel.getRecordings()();
  let tableBody = document.getElementById('recordings-data');
  tableBody.innerHTML = '';
  recordings.forEach(async function (recording) {
    console.log(recording)
    let tr = document.createElement('tr');
    let deleteTd = document.createElement('td');
    let deleteButton = document.createElement('button');
    deleteButton.classList.add('btn', 'btn-danger');
    deleteButton.innerText = 'Löschen';
    deleteButton.addEventListener('click', async function () {
      let requestBody = {
        tmdb_id: recording[12],
        is_movie: recording[13],
        season_number: recording[1],
        episode_number: recording[2],
        location_id: recording[11]
      };
      eel.deleteRecording(requestBody);
      await displayRecordings();
      // console.log(requestBody);
    });
    deleteTd.append(deleteButton);
    tr.append(deleteTd);
    // console.log(re// // cording)
    recording.forEach(async function (data, index) {
      if (index > 11) return;
      let td = document.createElement('td');
      let p = document.createElement('p');
      let tdContent = '';
      switch (index) {
        case 3:
          tdContent = data ? data.toString().substring(0, 30) + '...' : '';
          break;
        case 4:
        case 9:
          tdContent = data ? data.split('-').reverse().join('.') : '';
          break;
        case 5:
          tdContent = data ? 'ja' : 'nein';
          break;
        case 6:
          tdContent = data ? data.toString().replace('.', ',') : '';
          break;
        case 11:
          tdContent = await eel.getFullLocationById(data)();
          break;
        default:
          tdContent = data;
          break;
      }
      p.innerText = tdContent;
      td.append(p);
      // TODO: Add recording form
      if ((index < 1 || index > 2) && index != 11) {
        let updateContainer = document.createElement('div');
        updateContainer.classList.add('d-none');
        let updateInput = [3, 7, 10].includes(index) ? document.createElement('textarea') : (index == 11 ? document.createElement('select') : document.createElement('input'));
        switch (index) {
          case 0:
            updateInput.type = 'text';
            break;
          case 4:
          case 9:
            updateInput.type = 'date';
            break;
          case 5:
            updateInput.type = 'checkbox';
            break;
          case 6:
            updateInput.type = 'number';
            updateInput.step = '0.01';
            break;
          case 8:
            updateInput.type = 'number';
            updateInput.step = '1';
            break;
          case 11:
            locations.forEach(function (location) {
              let option = document.createElement('option');
              option.value = location[0];
              option.innerText = location[1];
              updateInput.append(option);
            });
            break;
          default:
            break;
        }
        if (index == 5) {
          if (data) updateInput.classList.add('checked');
        } else {
          updateInput.value = data;
        }
        let updateButton = document.createElement('button');
        updateButton.classList.add('btn', 'btn-secondary');
        updateButton.innerText = 'Speichern';
        updateContainer.append(updateInput);
        updateContainer.append(updateButton);
        td.append(updateContainer);
        td.addEventListener('click', function (e) {
          // console.log(e)
          let currentDiv = this.querySelector('div');
          if (currentDiv.classList.contains('d-none')) {
            this.querySelector('p').classList.toggle('d-none');
            currentDiv.classList.toggle('d-none');
          }
        });
        updateButton.addEventListener('click', async function (e) {
          e.stopPropagation();
          let currentTr = this.closest('tr');
          let currentTd = this.closest('td');
          let newVal;
          newVal = index == 5 ? updateInput.checked : updateInput.value;
          let requestBody = {
            tmdb_id: recording[12],
            is_movie: recording[13],
            season_number: currentTr.children[2].querySelector('p').innerText,
            episode_number: currentTr.children[3].querySelector('p').innerText,
            location_id: recording[11],
            index: index,
            data: newVal
          }
          eel.updateStorement(requestBody);
          let updatedVal;
          switch (index) {
            case 3:
              updatedVal = newVal.substring(0, 30) + '...';
              break;
            case 4:
            case 9:
              updatedVal = newVal.split('-').reverse().join('.');
              break;
            case 5:
              updatedVal = newVal ? 'ja' : 'nein';
              break;
            case 6:
              updatedVal = newVal.toString().replace('.', ',');
              break;
            default:
              updatedVal = newVal;
              break;
          }
          currentTd.querySelector('p').innerText = updatedVal;
          currentTd.querySelector('p').classList.toggle('d-none');
          currentTd.querySelector('div').classList.toggle('d-none');
        });
      }

      tr.append(td);
    });
    tableBody.append(tr);
  });
}

document.querySelector('.nav-link[data-link=recordings]').addEventListener('click', async function() {
  await fillAddRecordingForm();
  await displayRecordings();
});