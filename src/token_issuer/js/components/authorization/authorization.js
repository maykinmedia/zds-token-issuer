import BEM from 'bem.js';

const BLOCK_AUTHORIZATION_FORMS = BEM.getBEMNodes('set-auth');


/**
 * Names of fields that are always visible
 * @type {Array}
 */
const STATIC_FIELDS = [
    'client_id',
    'component',
    'scopes',
];

/**
 * Configuration that determines which fields/scope prefixes apply per
 * component type.
 * @type {Object}
 */
const CONFIG = {
    'AC': {
        fields: [],
        scopePrefixes: ['autorisaties'],
    },
    'NRC': {
        fields: [],
        scopePrefixes: ['notificaties'],
    },

    'ZRC': {
        fields: ['zaaktype', 'max_vertrouwelijkheidaanduiding'],
        scopePrefixes: ['zaken', 'notificaties', 'audittrails'],
    },
    'DRC': {
        fields: ['informatieobjecttype', 'max_vertrouwelijkheidaanduiding'],
        scopePrefixes: ['documenten', 'notificaties', 'audittrails'],
    },
    'ZTC': {
        fields: [],
        scopePrefixes: ['zaaktypes', 'notificaties', 'audittrails'],
    },
    'BRC': {
        fields: ['besluittype'],
        scopePrefixes: ['besluiten', 'notificaties', 'audittrails'],
    },
    'KC': {
        fields: [],
        scopePrefixes: ['klanten', 'audittrails'],
    },
    'VRC': {
        fields: [],
        scopePrefixes: ['verzoeken', 'audittrails'],
    },
    'CMC': {
        fields: [],
        scopePrefixes: ['contactmomenten', 'audittrails'],
    },
    'ORC': {
        fields: [],
        scopePrefixes: [],
    },
};


class SetAuth {
    constructor(node) {
        this.node = node;

        this.bindEvents();
    }

    bindEvents() {
        const componentSelect = this.node.querySelector('[name=component]');
        componentSelect.addEventListener(
            'change', (event) => this.handleComponentChange(event)
        );

        const event = new Event('change');
        componentSelect.dispatchEvent(event);
    }

    handleComponentChange(event) {
        const value = event.target.value.toUpperCase();
        const config = CONFIG[value];

        const visibleFields = STATIC_FIELDS.concat(config.fields);

        // set visibility of each field
        [...this.node.querySelectorAll('.form__control')]
            .map(node => {
                const dropdown = node.querySelector('.form__dropdown');
                if (!dropdown) {
                    return;
                }

                const visible = visibleFields.includes(dropdown.name);

                // reset the value if invisible
                if (!visible && dropdown.value) {
                    dropdown.value = '';
                }

                // let the CSS hide it
                node.classList.toggle('form__control--hidden', !visible);
            });

        // limit the scopes that are visible
        const scopes = [...this.node.querySelectorAll('input[name="scopes"]')];

        scopes.map(input => {
            let visible = false;
            config.scopePrefixes.map(prefix => {
                if (input.value.startsWith(`${prefix}.`)) {
                    visible = true;
                }
            });
            input.parentNode.classList.toggle('list__item--hidden', !visible);
        });
    }
}


[...BLOCK_AUTHORIZATION_FORMS].forEach(setAuth => new SetAuth(setAuth));
