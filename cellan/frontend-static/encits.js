/* global $ Plotly location history */

const page = {
  basePath: null,
  encodingId: 0,
  encoding: null,
  iteration: 0,
  duplicatesLookup: null,
  cell: null,
  geneFocus: null,
  threshold: 0,
  cids: null,
  originalColors: null,
  graphType: null
}

const transparentColor = 'rgba(0,0,0,0)'
const layout = {
  showlegend: false,
  margin: { t: 0, l: 25, b: 25, r: 0 },
  hovermode: 'closest',
  plot_bgcolor: transparentColor,
  paper_bgcolor: transparentColor,
  modebar: {
    color: 'darkgray',
    activecolor: 'black',
    bgcolor: transparentColor
  },
  xaxis: { range: [0, 255] },
  yaxis: { range: [0, 255] }
}
const display = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['resetScale2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displaylogo: false
}

const traces = (ids, text, x, y, z) => [{
  x: [],
  y: [],
  z: [],
  visible: false,
  mode: 'markers',
  type: page.graphType,
  hoverinfo: 'none',
  marker: {
    size: 14,
    color: 'lightgray',
    line: { color: 'darkgray', width: 2 }
  }
}, {
  ids,
  text,
  x,
  y,
  z,
  mode: 'markers',
  type: page.graphType,
  hoverinfo: 'text',
  marker: createDefaultMarkerOption(z)
}]

const createDefaultMarkerOption = color => {
  return {
    size: 4,
    color,
    colorscale: 'Portland',
    cmin: 0,
    cmax: 255,
    showscale: true,
    colorbar: {
      thickness: 7, xpad: 2, ypad: 0, len: 0.95, y: 0.95, yanchor: 'top'
    }
  }
}

const getDuplicateEntry = cellId => page.duplicatesLookup.find(d => d.cid === cellId)

$(() => {
  setPageDataFromUrl()
  addLoadListeners()
  loadIterationsSelect()
  addGraphTypeListeners()
  updatePlot()
  $(window).on('popstate', () => {
    setPageDataFromUrl()
    updatePlot()
  })
})

const addLoadListeners = () => {
  $('#threshold').change(() => {
    updatePageThreshold()
    updateCellDetails()
  })
  updatePageThreshold()

  const dupCellsSelect = $('#duplicate-cell-ids')
  dupCellsSelect.change(() => {
    const cellId = dupCellsSelect.find(':selected').val()
    return loadCellDetails(cellId)
  })
}

const updatePageThreshold = () => { page.threshold = parseInt($('#threshold').val()) }

const setPageDataFromUrl = () => {
  const segments = $(location).attr('href').split('/')
  page.iteration = segments.pop()
  page.encodingId = segments.pop()
  page.basePath = segments.join('/')
}

const loadIterationsSelect = () => ensureEncoding().then(() => {
  const iterationSelect = $('#iterations')
  iterationSelect.empty()
  page.encoding.showits.forEach(it => iterationSelect.append(`<option>${it}</option>`))
  iterationSelect.change(updateIteration)
  $('#iterations').val(page.iteration)
})

const updateIteration = () => {
  page.iteration = $('#iterations').find(':selected').text()
  const newLocation = $(location).attr('href').replace(/([0-9]*)$/, page.iteration)
  history.pushState(null, '', newLocation)
  updatePlot()
}

const graphType = {
  _2D: 'scattergl',
  _3D: 'scatter3d'
}

const addGraphTypeListeners = () => {
  page.graphType = graphType._2D
  $('#t2d').click(() => {
    page.graphType = graphType._2D
    show3DGraphType()
    updatePlot()
  })
  $('#t3d').click(() => {
    page.graphType = graphType._3D
    show2DGraphType()
    updatePlot()
  })
}

const updatePlot = () => {
  showLoader()
  return getEncodingIteration(page.encodingId, page.iteration)
    .then(encIteration => {
      page.cids = encIteration.cids
      page.originalColors = Array.from(encIteration.zs)
      updateDuplicates(encIteration)
      const traces = createTracePoints(encIteration)

      const graphDiv = getPlotDiv()
      Plotly.newPlot(graphDiv, traces, layout, display)
      graphDiv.on('plotly_click', ev => {
        const point = ev.points[0]
        if (!point.id) { return }
        highlightPoint(point.x, point.y, point.z)
        loadCellDetails(point.id)
      })
      graphDiv.on('plotly_afterplot', hideLoader)
    })
}

const updateDuplicates = encIteration => {
  page.duplicatesLookup = []
  encIteration.ds.forEach(dups => dups.forEach(dupCellId => {
    const pointIx = encIteration.cids.indexOf(dupCellId)
    const name = encIteration.ns[pointIx]
    page.duplicatesLookup.push({ cid: dupCellId, name, cids: dups })
  }))
}

const createTracePoints = encIteration => {
  const text = encIteration.ns.map((name, ix) => {
    const cellId = encIteration.cids[ix]
    const dups = getDuplicateEntry(cellId)
    const countText = (dups && `&nbsp;&nbsp;&nbsp;&nbsp;(${dups.cids.length} dups)`) || ''
    return `${name}<br>${cellId}${countText}`
  })
  return traces(encIteration.cids, text, encIteration.xs, encIteration.ys, encIteration.zs)
}

const highlightPoint = (x, y, z) => {
  const update = { x: [[x]], y: [[y]], z: [[z]], visible: true }
  setTimeout(() => Plotly.restyle(getPlotDiv(), update, [0]), 200)
}

const loadCellDetails = cellId => {
  showLoader()
  return getCell(cellId)
    .then(cell => {
      page.cell = cell
      updateCellDetails()
    })
    .always(hideLoader)
}

const updateCellDetails = () => {
  if (page.cell && Number.isInteger(page.threshold)) {
    updateCellDetailsHeader()
    const genesTable = $('#cell-genes')
    const template = $('.gene-template').first()
    genesTable.empty()
    genesTable.append(page.cell.g
      .filter(gene => gene.v >= page.threshold)
      .map(gene => {
        const geneRow = template.clone()
        geneRow.find('.ensembl').text(gene.e)
        geneRow.find('.mgi').text(gene.m)
        geneRow.find('.gval').text(gene.v)
        return geneRow
      })
    )
    formatCellGenes()
  }
}

const updateCellDetailsHeader = () => {
  const dupsEntry = getDuplicateEntry(page.cell.cid)
  if (dupsEntry) {
    showDuplicateCells()
    const cellSelect = $('#duplicate-cell-ids')
    cellSelect.empty()
    cellSelect.append(dupsEntry.cids.map(cid => {
      const name = getDuplicateEntry(cid).name
      return `<option value="${cid}">${cellDisplayName(cid, name)}</option>`
    }))
    cellSelect.val(page.cell.cid)
  } else {
    showSingleCell()
    $('#single-cell-id').text(cellDisplayName(page.cell.cid, page.cell.n))
  }
}

const cellDisplayName = (id, name) => `${name} (#${id})`

const updateGeneFocus = row => {
  const geneId = $(row).find('.ensembl').text()
  if (!geneId || geneId === page.geneFocus) {
    hideClearFilter()
    page.geneFocus = null
    recolorCellPoints(page.originalColors)
  } else {
    showClearFilter()
    showLoader()
    return getGene($(row).find('.ensembl').text())
      .then(gene => {
        page.geneFocus = gene.e
        const newColors = page.cids.map((cellId, ix) =>
          gene.cids.includes(cellId) ? page.originalColors[ix] : 'lightgrey'
        )
        recolorCellPoints(newColors)
      })
  }
}

const recolorCellPoints = newColors => {
  formatCellGenes()
  const update = { marker: createDefaultMarkerOption(newColors) }
  Plotly.restyle(getPlotDiv(), update, [1])
}

const formatCellGenes = () => {
  const tableRows = $('tr.gene-template')
  tableRows.removeClass('highlight')
  tableRows.each((_, v) => {
    const row = $(v)
    if (row.find('.ensembl').text() === page.geneFocus) {
      row.addClass('highlight')
    }
  })
}

// --- API calls ----------------------------
const apiGet = sub => $.get(`${page.basePath}/api/${sub}`)

const ensureEncoding = () => page.encoding
  ? $.Deferred().resolve()
  : apiGet(`encoding/${page.encodingId}`)
    .then(encoding => { page.encoding = encoding })

const getEncodingIteration = (encId, it) => apiGet(`encit/${encId}/${it}`)
const getCell = cid => ensureEncoding()
  .then(() => apiGet(`cell/${page.encoding.srcs.barcodes}/${cid}`))
const getGene = ensembl => ensureEncoding()
  .then(() => apiGet(`gene/${page.encoding.srcs.barcodes}/${ensembl}`))

// --- UI elements access ----------------------------
const getPlotDiv = () => $('#cell-graph').get(0)
const showLoader = () => $('#loader').removeClass('d-none')
const hideLoader = () => $('#loader').addClass('d-none')

const showSingleCell = () => {
  $('#single-cell-row').removeClass('d-none')
  $('#duplicate-cells-row').addClass('d-none')
}

const showDuplicateCells = () => {
  $('#single-cell-row').addClass('d-none')
  $('#duplicate-cells-row').removeClass('d-none')
}

const showClearFilter = () => $('#clear-focus').removeClass('d-none')
const hideClearFilter = () => $('#clear-focus').addClass('d-none')

const show2DGraphType = () => {
  $('#t2d').removeClass('disabled')
  $('#t3d').addClass('disabled')
}

const show3DGraphType = () => {
  $('#t2d').addClass('disabled')
  $('#t3d').removeClass('disabled')
}
