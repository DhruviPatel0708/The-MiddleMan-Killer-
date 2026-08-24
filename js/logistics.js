/**
 * THE MIDDLEMAN KILLER - Logistics Tracking & Telemetry Engine
 * Features explicit Gujarat State Highlighting vs Rest of India & Interactive Map Mode Toggle
 */

window.MKLogistics = {
    map: null,
    marker: null,
    tileLayer: null,
    maskLayer: null,
    gujaratLayer: null,
    
    // Toggle States
    isGujaratFocus: true,
    currentTileStyle: 'dark', // 'dark', 'light', 'satellite'

    initMap() {
        const mapContainer = document.getElementById('logisticsMap');
        if (!mapContainer) return;

        // Inject custom CSS for map overlays and glowing Gujarat highlight
        if (!document.getElementById('gujaratMapStyles')) {
            const style = document.createElement('style');
            style.id = 'gujaratMapStyles';
            style.innerHTML = `
                .gujarat-highlight-glow path {
                    stroke: #D6A84F !important;
                    stroke-width: 3.5px !important;
                    filter: drop-shadow(0 0 10px #D6A84F) drop-shadow(0 0 20px rgba(46, 204, 113, 0.7)) !important;
                    animation: gujaratBorderPulse 2.5s infinite alternate ease-in-out !important;
                }

                @keyframes gujaratBorderPulse {
                    0% {
                        stroke: #D6A84F;
                        fill-opacity: 0.16;
                    }
                    100% {
                        stroke: #2ECC71;
                        fill-opacity: 0.28;
                    }
                }

                .gujarat-state-badge {
                    background: linear-gradient(135deg, rgba(18, 55, 42, 0.95), rgba(5, 12, 8, 0.95));
                    border: 2px solid #D6A84F;
                    box-shadow: 0 0 20px rgba(214, 168, 79, 0.6);
                    color: #F8F6F0;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-weight: 800;
                    font-size: 0.78rem;
                    letter-spacing: 0.6px;
                    white-space: nowrap;
                    text-transform: uppercase;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    transform: translate(-50%, -50%);
                }

                .mandi-hub-dot {
                    width: 14px;
                    height: 14px;
                    background: #2ECC71;
                    border: 2px solid #FFFFFF;
                    border-radius: 50%;
                    box-shadow: 0 0 12px #2ECC71, 0 0 20px #2ECC71;
                    transform: translate(-50%, -50%);
                }

                .custom-truck-icon-inner {
                    background: #D96C3B;
                    width: 22px;
                    height: 22px;
                    border-radius: 50%;
                    border: 3px solid #FFFFFF;
                    box-shadow: 0 0 18px #D96C3B, 0 0 30px #D6A84F;
                    transform: translate(-50%, -50%);
                }

                .map-controls-overlay {
                    position: absolute;
                    top: 12px;
                    right: 12px;
                    z-index: 1000;
                    display: flex;
                    gap: 8px;
                }

                .map-toggle-btn {
                    background: rgba(18, 55, 42, 0.92);
                    color: #F4EFE4;
                    border: 1px solid rgba(214, 168, 79, 0.5);
                    padding: 7px 14px;
                    border-radius: 20px;
                    font-weight: 700;
                    font-size: 0.78rem;
                    cursor: pointer;
                    backdrop-filter: blur(8px);
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transition: all 0.2s ease;
                }

                .map-toggle-btn:hover {
                    background: rgba(217, 108, 59, 0.95);
                    border-color: #D96C3B;
                    color: #FFF;
                    transform: translateY(-1px);
                }
            `;
            document.head.appendChild(style);
        }

        // Check if Leaflet is available
        if (typeof L !== 'undefined') {
            if (this.map) this.map.remove();

            // Center on Gujarat state
            this.map = L.map('logisticsMap', {
                center: [22.5, 71.8],
                zoom: 7.2,
                zoomControl: true
            });

            // Set initial map tile style based on website theme
            const initialTheme = (window.MKApp && window.MKApp.currentTheme === 'light') ? 'light' : 'dark';
            this.setMapTileStyle(initialTheme);

            // Gujarat Boundary Coordinates
            const gujaratBoundary = [
                [23.71, 68.18],
                [23.85, 68.75],
                [24.00, 69.50],
                [24.45, 71.05],
                [24.70, 71.30],
                [24.55, 72.35],
                [24.25, 72.85],
                [24.00, 73.35],
                [23.60, 73.50],
                [23.35, 73.95],
                [22.80, 74.30],
                [22.15, 74.35],
                [21.85, 74.05],
                [21.35, 73.70],
                [20.70, 73.25],
                [20.25, 72.90],
                [20.50, 72.75],
                [21.05, 72.65],
                [21.40, 72.60],
                [21.75, 72.50],
                [21.45, 72.10],
                [21.00, 71.85],
                [20.70, 70.95],
                [21.00, 70.20],
                [21.50, 69.60],
                [22.25, 68.95],
                [22.50, 69.10],
                [22.90, 70.00],
                [23.10, 70.25],
                [23.25, 69.80],
                [23.40, 68.70],
                [23.71, 68.18]
            ];

            // 1. INVERTED MASK POLYGON: Dims non-Gujarat regions
            const outerBounds = [
                [85, -180],
                [85, 180],
                [-85, 180],
                [-85, -180]
            ];

            this.maskLayer = L.polygon([outerBounds, gujaratBoundary], {
                color: '#000000',
                weight: 1,
                fillColor: '#050a07',
                fillOpacity: 0.68,
                interactive: false
            }).addTo(this.map);

            // 2. GUJARAT STATE HIGHLIGHT POLYGON: Glowing border & vibrant green fill
            this.gujaratLayer = L.polygon(gujaratBoundary, {
                color: '#D6A84F',
                weight: 3.5,
                fillColor: '#2ECC71',
                fillOpacity: 0.18,
                className: 'gujarat-highlight-glow'
            }).addTo(this.map);

            // 3. GUJARAT STATE BADGE IN MAP CENTER
            const gujaratBadgeIcon = L.divIcon({
                className: 'state-badge-container',
                html: `<div class="gujarat-state-badge"><span>🌾</span> GUJARAT STATE • DIRECT AGRI HUB</div>`,
                iconSize: [0, 0]
            });
            L.marker([23.1, 71.4], { icon: gujaratBadgeIcon }).addTo(this.map);

            // 4. GUJARAT MANDI HUBS MARKERS
            const gujaratMandis = [
                { name: "Anand APMC", coords: [22.5645, 72.9289], info: "Tobacco, Paddy & Wheat Hub" },
                { name: "Rajkot Mandi", coords: [22.3039, 70.8022], info: "Groundnut & Cotton Hub" },
                { name: "Unjha Market Yard", coords: [23.8037, 72.3917], info: "Export Cumin & Spices Hub" },
                { name: "Junagadh Yard", coords: [21.5222, 70.4579], info: "Groundnut & Sesame Hub" },
                { name: "Surat Terminal", coords: [21.1702, 72.8311], info: "Paddy & Export Processing" },
                { name: "Mehsana Hub", coords: [23.5880, 72.3693], info: "Castor & Cotton Hub" }
            ];

            const mandiDotIcon = L.divIcon({
                className: 'mandi-dot-wrapper',
                html: `<div class="mandi-hub-dot"></div>`,
                iconSize: [0, 0]
            });

            gujaratMandis.forEach(mandi => {
                const mandiMarker = L.marker(mandi.coords, { icon: mandiDotIcon }).addTo(this.map);
                mandiMarker.bindTooltip(`<b>${mandi.name}</b><br><span style="color:#D6A84F;">${mandi.info}</span>`, {
                    direction: 'top',
                    offset: [0, -10]
                });
            });

            // 5. IN-TRANSIT TRUCK SHIPMENT ROUTE
            const waypoints = [
                [22.5645, 72.9289], // Anand Farm
                [22.3072, 73.1812], // Vadodara Hub
                [23.2156, 72.6369]  // Gandhinagar Plant
            ];

            L.polyline(waypoints, {
                color: '#D96C3B',
                weight: 5,
                opacity: 0.9,
                dashArray: '8, 12'
            }).addTo(this.map);

            // Custom Glowing Truck Icon
            const truckIcon = L.divIcon({
                className: 'custom-truck-icon',
                html: `<div class="custom-truck-icon-inner"></div>`,
                iconSize: [0, 0]
            });

            this.marker = L.marker([22.45, 73.05], { icon: truckIcon }).addTo(this.map);
            this.marker.bindPopup("<b>TRK-8849-GJ</b><br>150 Qtl Paddy in Transit<br>Temp: 22°C (Nominal)").openPopup();

            // 6. RENDER FLOATING CONTROL BAR ON MAP
            this.renderMapToggleOverlay();

            // Fit bounds to Gujarat state boundary cleanly
            this.map.fitBounds(this.gujaratLayer.getBounds(), { padding: [20, 20] });
        }
    },

    renderMapToggleOverlay() {
        const parent = document.getElementById('logisticsMap');
        if (!parent) return;

        let overlay = parent.querySelector('.map-controls-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'map-controls-overlay';
            parent.appendChild(overlay);
        }

        overlay.innerHTML = `
            <button onclick="MKLogistics.toggleFocusMode()" class="map-toggle-btn" title="Toggle Gujarat Highlight / All-India View">
                <span>${this.isGujaratFocus ? '📍' : '🌐'}</span>
                <span>${this.isGujaratFocus ? 'Gujarat Focus' : 'All India View'}</span>
            </button>
            <button onclick="MKLogistics.cycleMapTileStyle()" class="map-toggle-btn" title="Cycle Map Tile Style (Dark / Light / Satellite)">
                <span>${this.currentTileStyle === 'dark' ? '🌙' : this.currentTileStyle === 'light' ? '☀️' : '🛰️'}</span>
                <span>${this.currentTileStyle.toUpperCase()} MAP</span>
            </button>
        `;
    },

    toggleFocusMode() {
        this.isGujaratFocus = !this.isGujaratFocus;
        if (this.isGujaratFocus) {
            if (this.maskLayer && this.map && !this.map.hasLayer(this.maskLayer)) {
                this.map.addLayer(this.maskLayer);
            }
            if (this.gujaratLayer && this.map) {
                this.map.fitBounds(this.gujaratLayer.getBounds(), { padding: [20, 20] });
            }
        } else {
            if (this.maskLayer && this.map && this.map.hasLayer(this.maskLayer)) {
                this.map.removeLayer(this.maskLayer);
            }
            if (this.map) {
                this.map.setView([22.5937, 78.9629], 5); // All India Overview
            }
        }
        this.renderMapToggleOverlay();
        if (window.MKApp) {
            window.MKApp.notify('MAP VIEW TOGGLED', this.isGujaratFocus ? 'Focused on Gujarat State Highlight' : 'Expanded to All-India Trade Routes', 'gold');
        }
    },

    cycleMapTileStyle() {
        const styles = ['dark', 'light', 'satellite'];
        const nextIdx = (styles.indexOf(this.currentTileStyle) + 1) % styles.length;
        this.setMapTileStyle(styles[nextIdx]);
        this.renderMapToggleOverlay();
        if (window.MKApp) {
            window.MKApp.notify('MAP THEME TOGGLED', `Map style updated to ${this.currentTileStyle.toUpperCase()}`, 'green');
        }
    },

    setMapTileStyle(styleName) {
        this.currentTileStyle = styleName;
        if (this.tileLayer && this.map) {
            this.map.removeLayer(this.tileLayer);
        }

        let tileUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
        let attr = '&copy; OpenStreetMap &copy; CARTO';

        if (styleName === 'light') {
            tileUrl = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
        } else if (styleName === 'satellite') {
            tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
            attr = '&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP';
        }

        if (this.map) {
            this.tileLayer = L.tileLayer(tileUrl, { attribution: attr, maxZoom: 18 }).addTo(this.map);
        }
    }
};
