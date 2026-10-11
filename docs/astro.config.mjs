import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://nikomix.github.io',
  base: '/microhack-ai-platform',
  outDir: './dist',
  trailingSlash: 'always',
  integrations: [
    starlight({
      title: 'AI Platform TTT MicroHack',
      description: 'Train-the-Trainer MicroHack for the AI Platform on Microsoft Azure Specialization Module B controls.',
      customCss: ['./src/styles/custom.css'],
      social: [{ icon: 'github', label: 'GitHub repository', href: 'https://github.com/NikoMix/microhack-ai-platform' }],
      sidebar: [
        { label: 'Start Here', items: [{ label: 'Overview', slug: 'index' }] },
        {
          label: 'Trainer Guide',
          items: [
            { label: 'Run of Show', slug: 'trainer-guide/run-of-show' },
            { label: 'Facilitation Guide', slug: 'trainer-guide/facilitation' },
            { label: 'Grading Rubric', slug: 'trainer-guide/grading-rubric' }
          ]
        },
        {
          label: 'Labs',
          items: [
            { label: 'Lab 0: Setup', slug: 'labs/lab-0-setup' },
            { label: 'Lab 1: Assess', slug: 'labs/lab-1-assess' },
            { label: 'Lab 2: Design RAI', slug: 'labs/lab-2-design-rai' },
            { label: 'Lab 3: Well-Architected', slug: 'labs/lab-3-well-architected' },
            { label: 'Lab 4: PoC', slug: 'labs/lab-4-poc' },
            { label: 'Lab 5: Deploy', slug: 'labs/lab-5-deploy' },
            { label: 'Lab 6: Validate', slug: 'labs/lab-6-validate' },
            { label: 'Lab 7: Operate', slug: 'labs/lab-7-operate' },
            { label: 'Lab X: Azure Migration', slug: 'labs/lab-x-migration' }
          ]
        },
        {
          label: 'Concepts',
          items: [
            { label: 'Modular Inference', slug: 'concepts/modular-inference' },
            { label: 'Copilot Agents and Skills', slug: 'concepts/copilot-agents-skills' },
            { label: 'MCP Servers', slug: 'concepts/mcp-servers' },
            { label: 'GitHub Models', slug: 'concepts/github-models' },
            { label: 'Azure AI Foundry', slug: 'concepts/azure-ai-foundry' },
            { label: 'Agent Framework', slug: 'concepts/agent-framework' },
            { label: 'Responsible AI', slug: 'concepts/responsible-ai' }
          ]
        },
        { label: 'Reference', items: [{ label: 'Module B Mapping', slug: 'reference/module-b-mapping' }] }
      ]
    })
  ]
});
