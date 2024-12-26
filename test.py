from nicegui import ui
from typing import List, Dict
from datetime import datetime
import random
import pandas as pd
import io

PROJECTS = ['Project A', 'Project B', 'Project C']
STATUSES = ['In Progress', 'Completed', 'On Hold']
TAG_COLORS = {
    'High Priority': '#ff6b6b80',
    'Low Priority': '#4ecdc480',
    'Bug': '#ffd93d80',
    'Feature': '#6c5ce780',
    'Documentation': '#a8e6cf80'
}


class RadarTracker:
    def __init__(self):
        self.data = self.generate_sample_data()
        self.filtered_data = self.data.copy()
        self.selected_project = PROJECTS[0]
        self.status_filter = None
        self.tag_filter = None
        self.search_query = ""
        self.current_view = 'main'
        self.container = None

        self.columns = [
            {'name': 'radar_link', 'label': 'Radar ID', 'field': 'radar_link', 'align': 'left', 'sortable': True},
            {'name': 'title', 'label': 'Title', 'field': 'title', 'align': 'left', 'sortable': True},
            {'name': 'dri', 'label': 'DRI', 'field': 'dri', 'align': 'left', 'sortable': True},
            {'name': 'team_dri', 'label': 'Team', 'field': 'team_dri', 'align': 'left', 'sortable': True},
            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left', 'sortable': True},
            {'name': 'tags', 'label': 'Tags', 'field': 'tags', 'align': 'left'},
            {'name': 'comments', 'label': 'Comments', 'field': 'comments', 'align': 'left'}
        ]

        self.setup_ui()

    def generate_sample_data(self) -> List[Dict]:
        return [{
            'id': f'RAD-{i}',
            'radar_link': f'RAD-{i}',
            'title': f'Sample Radar {i}',
            'dri': f'Person {i}',
            'team_dri': f'Team {i}',
            'status': random.choice(STATUSES),
            'tags': [{'text': tag, 'color': TAG_COLORS[tag]}
                     for tag in random.sample(list(TAG_COLORS.keys()), 2)],
            'comments': f'Initial comment {i}',
            'history': [{
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'field': 'Initial',
                'old_value': '',
                'new_value': 'Created'
            }]
        } for i in range(1, 21)]

    def setup_ui(self):
        self.setup_header()
        with ui.element('div').classes('w-full max-w-7xl mx-auto px-4') as self.container:
            pass
        self.update_view()

    def update_view(self):
        self.container.clear()
        if self.current_view == 'main':
            self.setup_main_view()
        elif self.current_view == 'data':
            self.setup_data_view()
        elif self.current_view == 'stats':
            self.setup_stats_view()

    def switch_view(self, view: str):
        if self.current_view != view:
            self.current_view = view
            self.update_view()

    def setup_header(self):
        with ui.header().classes('bg-blue-600 text-white items-center'):
            ui.label('Radar Tracking System').classes('text-h6 q-px-md')
            with ui.row().classes('items-center'):
                ui.select(
                    PROJECTS,
                    value=self.selected_project,
                    on_change=lambda e: self.update_project(e.value)
                ).classes('q-px-md text-sm')

                ui.button('Main View', on_click=lambda: self.switch_view('main')).props('flat').classes('text-sm')
                ui.button('Statistics', on_click=lambda: self.switch_view('stats')).props('flat').classes('text-sm')
                ui.button('Data Management', on_click=lambda: self.switch_view('data')).props('flat').classes('text-sm')

    def setup_main_view(self):
        with self.container:
            self.setup_stats_cards()

            with ui.row().classes('w-full items-center justify-between my-2'):
                ui.input(placeholder='Search...', on_change=self.handle_search).classes('w-64 text-sm')
                with ui.row().classes('gap-1'):
                    for tag in TAG_COLORS:
                        self.create_filter_chip(tag, is_status=False)

            with ui.button(icon='menu').classes('my-2'):
                with ui.menu(), ui.column().classes('gap-0 p-2'):
                    for column in self.columns:
                        ui.switch(
                            column['label'],
                            value='classes' not in column or not column['classes'],
                            on_change=lambda e, col=column: self.toggle_column(col, e.value)
                        )

            self.create_table()

    def setup_stats_view(self):
        with self.container:
            ui.label('Detailed Statistics').classes('text-2xl font-bold mb-4')
            self.setup_stats_cards()

    def setup_data_view(self):
        with self.container:
            with ui.card().classes('w-full my-4'):
                ui.label('Data Management').classes('text-lg font-bold mb-4')

                with ui.row().classes('gap-4'):
                    with ui.column().classes('w-1/2'):
                        ui.label('Export Data').classes('text-sm font-bold')
                        ui.button('Export to CSV', on_click=self.export_data).classes('my-2')

                    with ui.column().classes('w-1/2'):
                        ui.label('Import Data').classes('text-sm font-bold')
                        ui.upload(
                            label='Upload CSV',
                            on_upload=self.import_data,
                            auto_upload=True
                        ).props('accept=.csv').classes('my-2')

    def setup_stats_cards(self):
        status_counts = {status: len([r for r in self.data if r['status'] == status])
                         for status in STATUSES}

        with ui.row().classes('w-full gap-4 my-4'):
            for status in STATUSES:
                is_selected = self.status_filter == status
                with ui.card().classes(
                        'w-48 cursor-pointer transition-colors hover:bg-blue-50'
                ).style(
                    f'background-color: {"#e6effd" if is_selected else "white"}; ' +
                    f'border: {"2px solid #2563eb" if is_selected else "1px solid #e5e7eb"};'
                ).on('click', lambda s=status: (
                        self.handle_filter(s, True),
                        self.update_view()
                )):
                    ui.label(status).classes(
                        f'text-lg font-bold {" text-blue-600" if is_selected else ""}')
                    ui.label(str(status_counts[status])).classes(
                        f'text-3xl {" text-blue-600" if is_selected else ""}')

    def create_filter_chip(self, value: str, is_status: bool):
        is_active = (self.status_filter == value) if is_status else (self.tag_filter == value)
        color = None if is_status else TAG_COLORS[value].replace('80', '')

        ui.button(
            value,
            on_click=lambda v=value: (
                self.handle_filter(v, is_status),
                self.update_view()
            )
        ).props(f'flat dense {"outline" if not is_active else ""}'
                ).classes(
            f'text-xs hover:bg-blue-50 {"bg-" + color if color and not is_active else "bg-blue-100" if is_active else ""}'
        )

    def toggle_column(self, column: Dict, visible: bool) -> None:
        column['classes'] = '' if visible else 'hidden'
        column['headerClasses'] = '' if visible else 'hidden'
        self.table.update()

    def create_table(self):
        self.table = ui.table(
            columns=self.columns,
            rows=self.filtered_data,
            row_key='id',
            pagination={'rowsPerPage': 15}
        ).classes('w-full')

        self.table.add_slot('header', '''
            <q-tr :props="props">
                <q-th auto-width />
                <q-th v-for="col in props.cols" :key="col.name" :props="props" 
                      class="py-0.5 px-1 text-xs">
                    {{ col.label }}
                </q-th>
            </q-tr>
        ''')

        self.table.add_slot('body', '''
            <q-tr :props="props" class="text-xs hover:bg-gray-50">
                <q-td auto-width class="py-0.5 px-1">
                    <q-btn size="sm" color="blue" round dense flat
                        @click="props.expand = !props.expand"
                        :icon="props.expand ? 'remove' : 'add'" />
                </q-td>
                <q-td v-for="col in props.cols" :key="col.name" :props="props" 
                      class="py-0.5 px-1" style="height: 24px;">
                    <template v-if="col.name === 'tags'">
                        <div class="flex gap-0.5">
                            <span v-for="tag in col.value" 
                                :key="tag.text" 
                                class="px-1 py-0.25 rounded text-xs"
                                :style="{ backgroundColor: tag.color }">
                                {{tag.text}}
                            </span>
                        </div>
                    </template>
                    <template v-else-if="col.name === 'comments'">
                        <q-input
                            v-model="props.row.comments"
                            dense
                            borderless
                            type="textarea"
                            class="text-xs"
                            style="line-height: 1;"
                            @update:model-value="$emit('update:comment', 
                                                     { id: props.row.id, value: $event })"
                        />
                    </template>
                    <template v-else>
                        {{ col.value }}
                    </template>
                </q-td>
            </q-tr>
            <q-tr v-show="props.expand" :props="props">
                <q-td colspan="100%">
                    <div class="text-left p-4">
                        <div class="text-lg font-bold mb-2">History</div>
                        <q-table
                            :rows="props.row.history"
                            :columns="[
                                {name: 'timestamp', label: 'Timestamp', field: 'timestamp', align: 'left'},
                                {name: 'field', label: 'Field', field: 'field', align: 'left'},
                                {name: 'old_value', label: 'Old Value', field: 'old_value', align: 'left'},
                                {name: 'new_value', label: 'New Value', field: 'new_value', align: 'left'}
                            ]"
                            row-key="timestamp"
                            dense
                            flat
                            bordered
                            hide-pagination
                            :rows-per-page="0"
                            class="text-xs"
                        />
                    </div>
                </q-td>
            </q-tr>
        ''')

        self.table.on('update:comment', self.update_comment)

    def handle_search(self, e):
        self.search_query = e.value.lower()
        self.apply_filters()

    def handle_filter(self, value: str, is_status: bool):
        if is_status:
            self.status_filter = None if self.status_filter == value else value
        else:
            self.tag_filter = None if self.tag_filter == value else value
        self.apply_filters()

    def apply_filters(self):
        self.filtered_data = self.data.copy()

        if self.search_query:
            self.filtered_data = [
                row for row in self.filtered_data
                if any(str(value).lower().find(self.search_query) != -1
                       for value in row.values() if isinstance(value, (str, int, float)))
            ]

        if self.status_filter:
            self.filtered_data = [row for row in self.filtered_data
                                  if row['status'] == self.status_filter]

        if self.tag_filter:
            self.filtered_data = [row for row in self.filtered_data
                                  if any(tag['text'] == self.tag_filter for tag in row['tags'])]

        self.update_table()

    def update_comment(self, e):
        row_id = e.args['id']
        new_comment = e.args['value']

        for row in self.data:
            if row['id'] == row_id:
                old_comment = row['comments']
                row['comments'] = new_comment
                row['history'].append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'field': 'comments',
                    'old_value': old_comment,
                    'new_value': new_comment
                })
                break

        self.apply_filters()

    def update_project(self, project: str):
        self.selected_project = project
        ui.notify(f'Switched to {project}')

    def update_table(self):
        if hasattr(self, 'table'):
            self.table.rows = self.filtered_data.copy()
            self.table.update()

    def export_data(self):
        # Prepare data
        export_data = []
        for row in self.filtered_data:
            export_row = row.copy()
            export_row['tags'] = ', '.join(tag['text'] for tag in row['tags'])
            export_row.pop('history', None)
            export_data.append(export_row)

        # Create CSV file
        df = pd.DataFrame(export_data)
        df.to_csv('radar_data.csv', index=False)

        # Download file
        ui.download('radar_data.csv')

    def import_data(self, e):
        content = e.content.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))
        imported_data = df.to_dict('records')

        # Convert imported data to match our structure
        for row in imported_data:
            # Convert tags string back to list of dicts
            if isinstance(row.get('tags'), str):
                tags = row['tags'].split(', ')
                row['tags'] = [{'text': tag, 'color': TAG_COLORS.get(tag, '#808080')}
                               for tag in tags]
            # Initialize history if not present
            if 'history' not in row:
                row['history'] = [{
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'field': 'Initial',
                    'old_value': '',
                    'new_value': 'Imported'
                }]

        self.data = imported_data
        self.filtered_data = self.data.copy()
        self.search_query = ""
        self.status_filter = None
        self.tag_filter = None
        self.update_table()
        ui.notify('Data imported successfully')


def main():
    RadarTracker()
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()