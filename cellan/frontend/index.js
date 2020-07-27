/* global $ Plotly location history */

const iterationOptions = Array.from({ length: 450 }, (_, ix) => 5009 + ix * 100)

const layout = {
  showlegend: false,
  margin: { t: 0, l: 0, b: 0, r: 0 },
  hovermode: 'closest'
}
const display = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['select2d', 'lasso2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displaylogo: false
}

const page = {
  encodingId: 0,
  cell: null,
  threshold: 0
}

$(() => {
  addThresholdListeners()
  loadIterationsSelect()
  loadEncodingFromUrl()
  $(window).on('popstate', loadEncodingFromUrl)
})

const addThresholdListeners = () => {
  $('#threshold').change(() => {
    updatePageThreshold()
    updateCellGenes()
  })
  updatePageThreshold()
}

const updatePageThreshold = () => { page.threshold = parseInt($('#threshold').val()) }

const loadIterationsSelect = () => {
  const iterationSelect = $('#iterations')
  iterationSelect.empty()
  iterationOptions.forEach(it => iterationSelect.append(`<option>${it}</option>`))
  iterationSelect.change(updateEncoding)
}

const loadEncodingFromUrl = () => {
  page.encodingId = $(location).attr('href').split('/').slice(-1).pop()
  $('#iterations').val(page.encodingId)
  updatePlot()
}

const updateEncoding = () => {
  page.encodingId = $('#iterations').find(':selected').text()
  const newLocation = $(location).attr('href').replace(/([0-9]*)$/, page.encodingId)
  history.pushState(null, '', newLocation)
  updatePlot()
}

const updatePlot = () => getEncodings(page.encodingId)
  .then(encodings => {
    const graphDiv = $('#cell-graph').get(0)
    const markers = createMarkers(encodings)

    Plotly.newPlot(graphDiv, markers, layout, display)
    graphDiv.on('plotly_click', ev => showCellDetails(ev.points[0]))
    graphDiv.on('plotly_afterplot', hideLoader)
  })

const createMarkers = encodings => {
  const text = encodings.ns.map((name, ix) => `${encodings.pids[ix]}<br>${name}`)
  return [{
    ids: encodings.pids,
    text,
    x: encodings.xs,
    y: encodings.ys,
    mode: 'markers',
    type: 'scattergl',
    hoverinfo: 'text',
    marker: {
      size: 4,
      color: encodings.zs,
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
        geneRow.find('.pval').text(gene.v)
        genesTable.append(geneRow)
      })
  }
}

const getEncodings = id => $.get(`api/encoding/${id}`)
const getCell = id => $.get(`api/cell/${id}`)

const showLoader = () => $('#loader').removeClass('invisible')
const hideLoader = () => $('#loader').addClass('invisible')
