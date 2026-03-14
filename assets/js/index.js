async function initLandingData() {
  try {
    const res = await fetch('./data/indices/itt_pulmon.json');
    if (!res.ok) throw new Error('No se pudo cargar itt_pulmon.json');
    const itt = await res.json();

    const estadoTxt = itt.meta?.version === 'preliminar' ? 'Preliminar' : 'Oficial';
    const ittGlobal = typeof itt.itt_global?.score === 'number' ? `${itt.itt_global.score.toFixed(1)}/100` : 'N/D';
    const variacion = typeof itt.itt_global?.variacion === 'number' ? `${itt.itt_global.variacion >= 0 ? '+' : ''}${itt.itt_global.variacion.toFixed(1)} pts` : 'N/D';

    document.getElementById('kpi-estado').innerText = estadoTxt;
    document.getElementById('kpi-itt-global').innerText = ittGlobal;
    document.getElementById('kpi-variacion').innerText = variacion;
  } catch (error) {
    console.error('Error cargando datos de ITT en index:', error);
    document.getElementById('kpi-estado').innerText = 'Preliminar';
    document.getElementById('kpi-itt-global').innerText = 'N/D';
    document.getElementById('kpi-variacion').innerText = 'N/D';
  }
}

initLandingData();
