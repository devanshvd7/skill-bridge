// UI Interaction Logic
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysis-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');
    const errorMsg = document.getElementById('error-msg');
    
    const resultsSection = document.getElementById('results-section');
    const userTags = document.getElementById('user-tags');
    const missingTags = document.getElementById('missing-tags');
    const summaryContent = document.getElementById('summary-content');
    const timeline = document.getElementById('timeline');
    
    const btnViewGraph = document.getElementById('btn-view-graph');
    const btnViewTimeline = document.getElementById('btn-view-timeline');
    const graphView = document.getElementById('graph-view');
    let cy = null;

    btnViewGraph.addEventListener('click', () => {
        btnViewGraph.classList.add('active');
        btnViewTimeline.classList.remove('active');
        graphView.classList.remove('hidden');
        timeline.classList.add('hidden');
        if (cy) cy.resize();
    });

    btnViewTimeline.addEventListener('click', () => {
        btnViewTimeline.classList.add('active');
        btnViewGraph.classList.remove('active');
        timeline.classList.remove('hidden');
        graphView.classList.add('hidden');
    });

    // Drag and Drop Logic
    setupDropZone('resume-zone', 'resume-file', 'resume-name');
    setupDropZone('job-zone', 'job-file', 'job-name');

    function setupDropZone(zoneId, inputId, nameId) {
        const zone = document.getElementById(zoneId);
        const input = document.getElementById(inputId);
        const nameDisplay = document.getElementById(nameId);

        // Click to open file dialog
        zone.addEventListener('click', () => input.click());

        // File selection
        input.addEventListener('change', (e) => handleFileSelect(e.target.files, zone, nameDisplay));

        // Drag events
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files; // Assign files to input
                handleFileSelect(e.dataTransfer.files, zone, nameDisplay);
            }
        });
    }

    function handleFileSelect(files, zone, nameDisplay) {
        if (files.length > 0) {
            const fileName = files[0].name;
            const validExts = ['.pdf', '.docx', '.txt', '.md'];
            const isValid = validExts.some(ext => fileName.toLowerCase().endsWith(ext));
            if (!isValid) {
                alert("Please upload a .pdf, .docx, .txt, or .md file.");
                return;
            }
            nameDisplay.textContent = fileName;
            zone.classList.add('has-file');
        } else {
            nameDisplay.textContent = '';
            zone.classList.remove('has-file');
        }
    }

    // JD Toggle Logic
    const toggleFileBtn = document.getElementById('toggle-file');
    const toggleTextBtn = document.getElementById('toggle-text');
    const jobFileSection = document.getElementById('job-file-section');
    const jobTextSection = document.getElementById('job-text-section');
    let jdMode = 'file'; // 'file' or 'text'

    toggleFileBtn.addEventListener('click', () => {
        jdMode = 'file';
        toggleFileBtn.classList.add('active');
        toggleTextBtn.classList.remove('active');
        jobFileSection.classList.remove('hidden');
        jobTextSection.classList.add('hidden');
    });

    toggleTextBtn.addEventListener('click', () => {
        jdMode = 'text';
        toggleTextBtn.classList.add('active');
        toggleFileBtn.classList.remove('active');
        jobTextSection.classList.remove('hidden');
        jobFileSection.classList.add('hidden');
    });

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const resumeFile = document.getElementById('resume-file').files[0];
        const jobFile = document.getElementById('job-file').files[0];
        const jdText = document.getElementById('jd-text').value;

        if (!resumeFile) {
            showError("A Resume is required.");
            return;
        }

        if (jdMode === 'file' && !jobFile) {
            showError("A Job Description file is required in File mode.");
            return;
        }

        if (jdMode === 'text' && !jdText.trim()) {
            showError("Job Description text is required in Paste mode.");
            return;
        }

        // Setup loading state
        setLoading(true);
        resultsSection.classList.add('hidden');
        errorMsg.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('resume', resumeFile);
            
            if (jdMode === 'file') {
                formData.append('job_description', jobFile);
            } else {
                formData.append('jd_text', jdText);
            }

            const response = await fetch('/analyze-gap', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            console.error(error);
            showError("Analysis failed. Make sure your server is running and API key is valid.");
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    }

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    // Result Rendering
    function renderResults(data) {
        // Render Tags
        userTags.innerHTML = data.user_skills.length 
            ? data.user_skills.map(skill => `<span class="tag">${skill}</span>`).join('')
            : '<span class="tag">No matching skills found</span>';
            
        missingTags.innerHTML = data.missing_skills.length
            ? data.missing_skills.map(skill => `<span class="tag">${skill}</span>`).join('')
            : '<span class="tag">You have all required skills!</span>';

        // Render Summary
        summaryContent.innerText = data.summary;

        // Render Flowchart / Timeline
        timeline.innerHTML = '';
        
        if (!data.roadmap.tiers || data.roadmap.tiers.length === 0) {
            timeline.innerHTML = `
                <div class="phase-block">
                    <div class="phase-marker">✓</div>
                    <div class="phase-content" style="text-align:center;">
                        <h3 class="phase-title" style="margin-bottom:0;">You are fully qualified! No roadmap necessary.</h3>
                    </div>
                </div>
            `;
        } else {
            data.roadmap.tiers.forEach(tier => {
                const isParallel = tier.skills.length > 1;
                
                let coursesHtml = tier.courses.map(course => `
                    <div class="course-card">
                        <span class="course-target">Target: ${course.teaches}</span>
                        <a href="${course.url}" target="_blank" class="course-link">
                            <div class="course-name">${course.title}</div>
                        </a>
                        <div class="course-meta">
                            <span>⏱️ ${course.duration_hours} hrs</span>
                        </div>
                    </div>
                `).join('');

                if (tier.courses.length === 0) {
                    coursesHtml = `
                    <div class="course-card">
                        <span class="course-target">Target: ${tier.skills.join(', ')}</span>
                        <div class="course-name" style="color:var(--text-muted)">Self-study recommended</div>
                    </div>`;
                }

                const phaseBlock = document.createElement('div');
                phaseBlock.className = 'phase-block';
                phaseBlock.innerHTML = `
                    <div class="phase-marker">${tier.phase}</div>
                    <div class="phase-content">
                        <div class="phase-header">
                            <h3 class="phase-title">Phase ${tier.phase}</h3>
                            ${isParallel ? '<span class="parallel-badge">Learn Parallel</span>' : ''}
                        </div>
                        <div class="skills-list">
                            ${coursesHtml}
                        </div>
                    </div>
                `;
                timeline.appendChild(phaseBlock);
            });
        }

        // Show section
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Render Interactive Graph
        renderGraph(data);
    }

    function renderGraph(data) {
        if (cy) cy.destroy();
        
        const completedSkills = new Set(Object.keys(data.user_skills || {}));
        const elements = [];
        
        data.all_skills.forEach(skill => {
            elements.push({ data: { id: skill, label: skill } });
        });
        
        data.graph_edges.forEach(edge => {
            elements.push({ data: { source: edge[0], target: edge[1] } });
        });
        
        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'color': '#fff',
                        'font-size': '12px',
                        'width': 'label',
                        'height': 'label',
                        'padding': '12px',
                        'shape': 'round-rectangle',
                        'background-color': '#475569',
                        'border-width': 2,
                        'border-color': '#334155',
                        'transition-property': 'background-color, border-color, shadow-blur',
                        'transition-duration': '0.3s'
                    }
                },
                {
                    selector: 'node.completed',
                    style: { 
                        'background-color': '#10b981',
                        'border-color': '#059669',
                        'shadow-blur': 10,
                        'shadow-color': '#10b981'
                    }
                },
                {
                    selector: 'node.available',
                    style: { 
                        'background-color': '#f59e0b',
                        'border-color': '#d97706',
                        'shadow-blur': 10,
                        'shadow-color': '#f59e0b'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#64748b',
                        'target-arrow-color': '#64748b',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'arrow-scale': 1.2
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                spacingFactor: 1.1
            }
        });
        
        function updateNodeColors() {
            cy.nodes().forEach(node => {
                const id = node.id();
                node.removeClass('completed available');
                
                if (completedSkills.has(id)) {
                    node.addClass('completed');
                } else {
                    const incomings = node.incomers('node');
                    let depsMet = true;
                    incomings.forEach(inc => {
                        if (!completedSkills.has(inc.id())) depsMet = false;
                    });
                    if (depsMet) node.addClass('available');
                }
            });
        }
        
        updateNodeColors();
        
        cy.on('tap', 'node', function(evt){
            const id = evt.target.id();
            if (completedSkills.has(id)) {
                completedSkills.delete(id);
            } else {
                completedSkills.add(id);
            }
            updateNodeColors();
        });
    }
});
