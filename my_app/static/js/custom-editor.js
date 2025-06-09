// my_blog/static/js/custom-editor.js

class CustomMarkdownEditor {
    constructor(targetTextareaId) {
        this.textarea = document.getElementById(targetTextareaId);
        if (!this.textarea) {
            console.error(`Editor target textarea with id "${targetTextareaId}" not found.`);
            return;
        }

        this.container = null; // 编辑器最外层容器
        this.toolbar = null;   // 工具栏

        // ⭐ 新功能：定义代码块高亮主题
        this.codeThemes = [
            { name: '默认', class: '' },
            { name: '深海', class: 'code-theme-ocean' },
            { name: '熔岩', class: 'code-theme-lava' },
            { name: '赛博', class: 'code-theme-cyber' },
            { name: '绿光', class: 'code-theme-matrix' },
        ];

        this._createEditorLayout();
        this._createToolbarButtons();
    }

    /**
     * 创建编辑器的 HTML 骨架并替换原始的 textarea
     */
    _createEditorLayout() {
        // 1. 创建容器和工具栏
        this.container = document.createElement('div');
        this.container.className = 'custom-editor-container';

        this.toolbar = document.createElement('div');
        this.toolbar.className = 'custom-editor-toolbar';

        // 2. 将 textarea 移动到容器内部
        const parent = this.textarea.parentNode;
        this.container.appendChild(this.toolbar);
        this.container.appendChild(this.textarea);

        // 3. 将整个编辑器组件替换掉原来的 textarea 位置
        parent.replaceChild(this.container, this.textarea);

        // 4. 为 textarea 添加样式类
        this.textarea.className = 'custom-editor-textarea';
    }

    /**
     * 在工具栏中创建所有功能按钮
     */
    _createToolbarButtons() {
        const buttons = [
            { tag: 'B', title: '加粗', prefix: '**', suffix: '**' },
            { tag: 'I', title: '斜体', prefix: '*', suffix: '*' },
            { tag: 'H1', title: '一级标题', prefix: '# ', suffix: '' },
            { tag: 'H2', title: '二级标题', prefix: '## ', suffix: '' },
            { tag: '”', title: '引用', prefix: '> ', suffix: '' },
            { tag: '🔗', title: '链接', prefix: '[', suffix: '](https://)' },
            { tag: '🖼️', title: '图片', prefix: '![', suffix: '](https://)' },
            { tag: '`', title: '行内代码', prefix: '`', suffix: '`' },
            { tag: 'CODE', title: '代码块', action: () => this._handleCodeBlock() }
        ];

        buttons.forEach(b => {
            const button = document.createElement('button');
            button.type = 'button';
            button.innerHTML = b.tag;
            button.title = b.title;
            button.addEventListener('click', () => {
                if (b.action) {
                    b.action();
                } else {
                    this._insertMarkdown(b.prefix, b.suffix);
                }
            });
            this.toolbar.appendChild(button);
        });

        // ⭐ 创建代码块高亮主题选择器
        const themeSelector = this._createSelect(this.codeThemes, '选择高亮主题');
        themeSelector.id = 'code-theme-selector';
        this.toolbar.appendChild(themeSelector);
    }

    /**
     * 通用函数：创建一个 <select> 下拉菜单
     * @param {Array} options - 选项数组, e.g. [{name: '显示名', value: '实际值'}]
     * @param {string} title - 鼠标悬浮提示
     * @returns {HTMLSelectElement}
     */
    _createSelect(options, title) {
        const selector = document.createElement('select');
        selector.title = title;
        options.forEach(opt => {
            const option = document.createElement('option');
            // 如果 opt 是对象，则使用 name/class；否则直接使用 opt
            option.value = opt.class !== undefined ? opt.class : opt;
            option.textContent = opt.name !== undefined ? opt.name : opt;
            selector.appendChild(option);
        });
        return selector;
    }

    /**
     * 核心函数：插入 Markdown
     */
    _insertMarkdown(prefix, suffix = '') {
        const start = this.textarea.selectionStart;
        const end = this.textarea.selectionEnd;
        const selectedText = this.textarea.value.substring(start, end);
        const replacement = prefix + selectedText + suffix;

        this.textarea.value = this.textarea.value.substring(0, start) + replacement + this.textarea.value.substring(end);

        if (selectedText) {
            this.textarea.focus();
            this.textarea.setSelectionRange(start + replacement.length, start + replacement.length);
        } else {
            this.textarea.focus();
            this.textarea.setSelectionRange(start + prefix.length, start + prefix.length);
        }
        this.textarea.dispatchEvent(new Event('input'));
    }

    /**
     * 特殊处理代码块插入
     */
    _handleCodeBlock() {
        const selectedThemeClass = document.getElementById('code-theme-selector').value;
        // 注意：现在我们把高亮类加在 ``` 后面
        const prefix = '\n```' + selectedThemeClass + '\n';
        const suffix = '\n```\n';
        this._insertMarkdown(prefix, suffix);
    }
}