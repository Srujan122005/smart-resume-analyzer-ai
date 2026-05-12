// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('results-section');

    if (!analyzeBtn || !resultsSection) return;

    analyzeBtn.addEventListener('click', () => {
        // 1. Enter Loading State
        const originalContent = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = `<span class="animate-spin material-symbols-outlined">sync</span> Analyzing...`;
        analyzeBtn.disabled = true;

        // 2. Simulate AI Analysis Delay (1 second)
        setTimeout(() => {
            // 3. Transform Results UI
            // We change the layout from a centered placeholder to a structured report
            resultsSection.classList.remove('border-dashed', 'items-center', 'text-center');
            resultsSection.classList.add('border-solid', 'items-start', 'text-left');
            
            resultsSection.innerHTML = `
                <div class="w-full space-y-6 animate-in fade-in duration-500">
                    <div class="flex items-center justify-between border-b border-outline-variant pb-4">
                        <h2 class="font-headline-lg text-on-surface">Analysis Report</h2>
                        <div class="flex flex-col items-end">
                            <span class="text-label-md text-outline uppercase tracking-wider">Match Score</span>
                            <span class="text-2xl font-bold text-primary">75%</span>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-3">
                            <h3 class="font-headline-md text-on-surface flex items-center gap-2">
                                <span class="material-symbols-outlined text-error">dangerous</span>
                                Missing Skills
                            </h3>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-error-container text-on-error-container rounded-md text-sm font-medium">Python</span>
                                <span class="px-3 py-1 bg-error-container text-on-error-container rounded-md text-sm font-medium">Machine Learning</span>
                                <span class="px-3 py-1 bg-error-container text-on-error-container rounded-md text-sm font-medium">AWS SageMaker</span>
                            </div>
                        </div>

                        <div class="space-y-3">
                            <h3 class="font-headline-md text-on-surface flex items-center gap-2">
                                <span class="material-symbols-outlined text-tertiary-container">check_circle</span>
                                Strong Matches
                            </h3>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-md text-sm font-medium">Tailwind CSS</span>
                                <span class="px-3 py-1 bg-secondary-container text-on-secondary-container rounded-md text-sm font-medium">JavaScript (ES6+)</span>
                            </div>
                        </div>
                    </div>

                    <div class="p-4 bg-surface-container-highest rounded-lg border-l-4 border-primary">
                        <p class="text-on-surface-variant leading-relaxed">
                            <strong class="text-on-surface">AI Suggestion:</strong> Your resume is strong in frontend technologies, but the job description emphasizes backend data processing. Try highlighting any experience with <span class="text-primary">Python</span> or <span class="text-primary">API integration</span> to bridge the gap.
                        </p>
                    </div>

                    <button id="reset-btn" class="text-sm text-outline hover:text-primary flex items-center gap-1 transition-colors">
                        <span class="material-symbols-outlined text-sm">refresh</span> Try another resume
                    </button>
                </div>
            `;

            // 4. Reset Logic
            document.getElementById('reset-btn').addEventListener('click', () => {
                location.reload();
            });

            // 5. Restore Analyze Button
            analyzeBtn.innerHTML = originalContent;
            analyzeBtn.disabled = false;
        }, 1000);
    });
});