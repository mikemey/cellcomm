/* global $ Plotly location history */

const iterationOptions = Array.from({ length: 450 }, (_, ix) => 5009 + ix * 100)

const transparentColor = 'rgba(0,0,0,0)'
const layout = {
  showlegend: false,
  margin: { t: 0, l: 0, b: 0, r: 0 },
  hovermode: 'closest',
  plot_bgcolor: transparentColor,
  paper_bgcolor: transparentColor,
  modebar: {
    color: 'darkgray',
    activecolor: 'black',
    bgcolor: transparentColor
  }
}
const display = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['resetScale2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displaylogo: false
}

const page = {
  basePath: null,
  encodingId: 0,
  encoding: null,
  iteration: 0,
  cell: null,
  threshold: 0
}

$(() => {
  addThresholdListeners()
  loadIterationsSelect()
  loadDataFromUrl()
  $(window).on('popstate', loadDataFromUrl)
})

const addThresholdListeners = () => {
  $('#threshold').change(() => {
    updatePageThreshold()
    updateCellGenes()
  })
  updatePageThreshold()
}

const updatePageThreshold = () => { page.threshold = parseInt($('#threshold').val()) }

const loadDataFromUrl = () => {
  const segments = $(location).attr('href').split('/')
  page.iteration = segments.pop()
  page.encodingId = segments.pop()
  page.basePath = segments.join('/')
  $('#iterations').val(page.iteration)
  updatePlot()
}

const loadIterationsSelect = () => {
  const iterationSelect = $('#iterations')
  iterationSelect.empty()
  iterationOptions.forEach(it => iterationSelect.append(`<option>${it}</option>`))
  iterationSelect.change(updateIteration)
}

const updateIteration = () => {
  page.iteration = $('#iterations').find(':selected').text()
  const newLocation = $(location).attr('href').replace(/([0-9]*)$/, page.iteration)
  history.pushState(null, '', newLocation)
  updatePlot()
}

const updatePlot = () => {
  showLoader()
  return getEncodingIteration(page.encodingId, page.iteration)
    .then(cellPoints => {
      const graphDiv = $('#cell-graph').get(0)
      const markers = createMarkers(cellPoints)

      Plotly.newPlot(graphDiv, markers, layout, display)
      graphDiv.on('plotly_click', ev => showCellDetails(ev.points[0]))
      graphDiv.on('plotly_afterplot', hideLoader)
    })
}

const createMarkers = cellPoints => {
  const text = cellPoints.ns.map((name, ix) => `${cellPoints.cids[ix]}<br>${name}`)
  return [{
    ids: cellPoints.cids,
    text,
    x: cellPoints.xs,
    y: cellPoints.ys,
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    marker: {
      size: 4,
      color: cellPoints.zs,
      colorscale: 'Jet'
    }
  }]
}

const showCellDetails = point => {
  showLoader()
  const cellId = point.data.ids[point.pointIndex]
  return getCell(cellId)
    .then(cell => {
      page.cell = cell
      $('#cell-id').text(`${cell.n} (${cellId})`)
      updateCellGenes()
    })
    .always(hideLoader)
}

const updateCellGenes = () => {
  if (page.cell && Number.isInteger(page.threshold)) {
    const genesTable = $('#cell-genes')
    const template = $('.gene-template').first()
    genesTable.empty()
    page.cell.g
      .filter(gene => gene.v > page.threshold)
      .forEach(gene => {
        const geneRow = template.clone()
        geneRow.find('.ensemble').text(gene.e)
        geneRow.find('.mgi').text(gene.m)
        geneRow.find('.gval').text(gene.v)
        genesTable.append(geneRow)
      })
  }
}

const apiGet = sub => $.get(`${page.basePath}/api/${sub}`)

const ensureEncoding = () => page.encoding
  ? $.Deferred().resolve()
  : apiGet(`encoding/${page.encodingId}`)
    .then(encoding => { page.encoding = encoding })

const getEncodingIteration = (encId, it) => apiGet(`encit/${encId}/${it}`)
const getCell = cid => ensureEncoding()
  .then(() => apiGet(`cell/${page.encoding.src}/${cid}`))

const showLoader = () => $('#loader').removeClass('invisible')
const hideLoader = () => $('#loader').addClass('invisible')
