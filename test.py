# 2024/12/28 Ask why row space is limited as 48px

from nicegui import ui
from typing import List, Dict
from datetime import datetime
import random
import pandas as pd
import io

PROJECTS = ['Project A', 'Project B', 'Project C']
STATUSES = ['In Progress', 'Completed', 'On Hold']
TAG_COLORS = {
    'High Priority': 'background-color: rgba(255,99,71,0.2)',  # Light red
    'Low Priority': 'background-color: rgba(144,238,144,0.2)',  # Light green
    'Bug': 'background-color: rgba(255,215,0,0.2)',          # Light yellow
    'Feature': 'background-color: rgba(147,112,219,0.2)',    # Light purple
    'Documentation': 'background-color: rgba(135,206,250,0.2)' # Light blue
}
TEAM_MEMBERS = ['Person A', 'Person B', 'Person C', 'Person D', 'Person E']

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

        # Initialize row spacing
        self.row_spacing = 'dense'  # default value

        self.columns = [
            {'name': 'id', 'label': 'Radar ID', 'field': 'id', 'align': 'left', 'sortable': True},
            {'name': 'title', 'label': 'Title', 'field': 'title', 'align': 'left', 'sortable': True},
            {'name': 'dri', 'label': 'Current DRI', 'field': 'dri', 'align': 'left', 'sortable': True},
            {'name': 'team_dri', 'label': 'Team DRI', 'field': 'team_dri', 'align': 'left', 'sortable': True},
            {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'left', 'sortable': True},
            {'name': 'tags', 'label': 'Tags', 'field': 'tags', 'align': 'left'},
            {'name': 'comments', 'label': 'Comments', 'field': 'comments', 'align': 'left'}
        ]

        ui.add_head_html('''
            <style>
                .q-table tr, .q-table td {
                    min-height: unset !important;
                }
                .q-table--dense .q-td {
                    padding: 2px 4px !important;
                }
                /* Style for textarea */
                .q-field__native.q-placeholder {
                    white-space: pre-wrap !important;
                    resize: vertical !important;
                    overflow: auto !important;
                }
            </style>
        ''')

        self.setup_ui()

    def generate_sample_data(self) -> List[Dict]:
        return [{
            'id': f'radr://{i}',  # Changed to radar link format directly
            'title': f'Sample Radar {i}',
            'dri': f'Person {i}',
            'team_dri': TEAM_MEMBERS[i % len(TEAM_MEMBERS)],
            'status': random.choice(STATUSES),
            'tags': [{'text': tag, 'style': TAG_COLORS[tag]}
                     for tag in random.sample(list(TAG_COLORS.keys()), 2)],
            'comments_history': [{
                'id': f'comment-{i}-1',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'comment': f'Initial comment {i}',
                'author': TEAM_MEMBERS[i % len(TEAM_MEMBERS)]
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

            # Create a container for search, settings, and filters with proper spacing
            with ui.row().classes('w-full items-end justify-between mt-4 mb-6'):
                # Left side container
                with ui.row().classes('items-end gap-2'):
                    # Search input container with adjusted text position
                    with ui.input(
                            placeholder='Search...',
                            on_change=self.handle_search
                    ).props('borderless dense').classes('w-64') as search:
                        search.style(
                            'border-top: none; '
                            'border-left: none; '
                            'border-right: none; '
                            'border-bottom: 1px solid #e2e8f0; '
                            'border-radius: 0; '
                            'padding: 0 0 12px 0; '  # Increased bottom padding to move text up
                            'margin: 0; '
                            'height: 36px; '  # Increased height to accommodate padding
                            'min-height: 36px; '
                            'font-size: 14px; '
                            'line-height: 24px; '  # Adjusted line height for better positioning
                            'box-shadow: none; '
                            'background: transparent; '
                        )

                    # Settings button
                    with ui.button(icon='settings').props('flat dense').classes('text-sm'):
                        with ui.menu().classes('p-4 min-w-[250px]'):
                            # Row Spacing Section
                            with ui.column().classes('w-full gap-2'):
                                ui.label('Row Spacing').classes('text-sm font-bold text-gray-700')
                                ui.select(
                                    {
                                        'dense': 'Compact',
                                        'normal': 'Comfortable',
                                        'loose': 'Spacious'
                                    },
                                    value=getattr(self, 'row_spacing', 'dense'),
                                    on_change=self.change_row_spacing
                                ).classes('text-sm w-full')

                                # Divider with proper spacing
                                ui.separator().classes('my-3')

                                # Column Visibility Section
                                ui.label('Visible Columns').classes('text-sm font-bold text-gray-700')
                                for column in self.columns:
                                    with ui.row().classes('items-center justify-between w-full py-1'):
                                        ui.switch(
                                            text=column['label'],
                                            value='classes' not in column or not column['classes'],
                                            on_change=lambda e, col=column: self.toggle_column(col, e.value)
                                        ).classes('text-sm')

                # Right side: Tag filters
                with ui.row().classes('gap-1 items-end'):
                    for tag in TAG_COLORS:
                        self.create_filter_chip(tag, is_status=False)

            # Remove existing table if any
            if hasattr(self, 'table'):
                self.table.clear()
            # Create new table
            self.create_table()

    def setup_stats_view(self):
        with self.container:
            ui.label('Detailed Statistics').classes('text-2xl font-bold mb-4')

            # Setup the original stats cards
            self.setup_stats_cards()

            # Add time range selector for historical analysis
            with ui.row().classes('w-full items-center gap-4 my-4'):
                ui.label('Time Range:').classes('font-bold')
                time_range = ui.select(
                    options=['Last 7 Days', 'Last 30 Days', 'Last 3 Months', 'All Time'],
                    value='All Time'
                ).props('outlined dense')

                # Add refresh button
                ui.button(icon='refresh', on_click=lambda: self.refresh_stats()).props('flat')

            # Status Distribution with drill-down capability
            with ui.card().classes('w-full my-4 p-4'):
                ui.label('Status Distribution').classes('text-lg font-bold mb-4')

                status_counts = {status: len([r for r in self.filtered_data if r['status'] == status])
                                 for status in STATUSES}

                # Interactive pie chart with click events
                chart = ui.plotly({
                    'data': [{
                        'values': list(status_counts.values()),
                        'labels': list(status_counts.keys()),
                        'type': 'pie',
                        'hole': 0.4,
                        'marker': {'colors': ['#4299e1', '#48bb78', '#f6ad55']},
                        'textinfo': 'label+percent',
                        'textposition': 'outside',
                    }],
                    'layout': {
                        'height': 400,
                        'showlegend': True,
                        'legend': {'orientation': 'h', 'y': -0.1},
                        'margin': {'t': 30, 'b': 40, 'l': 40, 'r': 40}
                    }
                }).classes('w-full')

                # Add click handler for drill-down
                async def handle_chart_click(e):
                    status = e.node.get('label')
                    details = [r for r in self.filtered_data if r['status'] == status]
                    await self.show_status_details(status, details)

                chart.on('plotly_click', handle_chart_click)

                # Add Tag Distribution Chart
                ui.label('Tag Distribution').classes('text-lg font-bold mt-8 mb-4')

                # Calculate tag distribution
                tag_counts = {}
                for row in self.filtered_data:
                    for tag in row['tags']:
                        tag_text = tag['text']
                        tag_counts[tag_text] = tag_counts.get(tag_text, 0) + 1

                # Create interactive bar chart
                ui.plotly({
                    'data': [{
                        'x': list(tag_counts.keys()),
                        'y': list(tag_counts.values()),
                        'type': 'bar',
                        'marker': {
                            'color': [TAG_COLORS[tag].replace('rgba', 'rgb').replace(',0.2)', ',0.6)')
                                      for tag in tag_counts.keys()]
                        }
                    }],
                    'layout': {
                        'height': 300,
                        'margin': {'t': 20, 'b': 60, 'l': 40, 'r': 20},
                        'xaxis': {
                            'title': 'Tags',
                            'tickangle': -45
                        },
                        'yaxis': {
                            'title': 'Count'
                        },
                        'bargap': 0.3
                    }
                }).classes('w-full')

    async def show_status_details(self, status: str, details: list):
        """Show detailed modal for clicked status"""
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Details for {status} Items').classes('text-xl font-bold mb-4')

            # Create a table with detailed information
            ui.table(
                columns=[
                    {'name': 'radar_link', 'label': 'Radar ID', 'field': 'radar_link'},
                    {'name': 'title', 'label': 'Title', 'field': 'title'},
                    {'name': 'team_dri', 'label': 'Team', 'field': 'team_dri'},
                    {'name': 'dri', 'label': 'DRI', 'field': 'dri'}
                ],
                rows=details,
                pagination={'rowsPerPage': 5}
            ).classes('w-full')

            ui.button('Close', on_click=dialog.close).props('flat')

    def refresh_stats(self):
        """Refresh all statistics and charts"""
        self.update_view()

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
        style = None if is_status else TAG_COLORS[value]

        # Start with base styles
        base_classes = 'text-xs hover:bg-blue-50'
        active_classes = 'bg-blue-100'

        # Apply different styles based on whether it's a tag or status
        if not is_status:
            if is_active:
                # When tag is active, use a stronger version of the tag's color
                style = style.replace('0.2', '0.6')  # Make background more opaque
                button_classes = f'{base_classes} font-medium'  # Make text bolder when active
            else:
                button_classes = base_classes
        else:
            # For status filters
            button_classes = f'{base_classes} {active_classes if is_active else ""}'

        button = ui.button(
            value,
            on_click=lambda v=value: (
                self.handle_filter(v, is_status),
                self.update_view()
            )
        ).props(f'flat dense {"outline" if not is_active else ""}').classes(button_classes)

        # Apply style only if it exists
        if style:
            button.style(style)

        return button

    def toggle_column(self, column: Dict, visible: bool) -> None:
        column['classes'] = '' if visible else 'hidden'
        column['headerClasses'] = '' if visible else 'hidden'
        self.table.update()

    def create_table(self):
        spacing_config = {
            'dense': {'height': '48px', 'input_height': '28px'},
            'normal': {'height': '64px', 'input_height': '36px'},
            'loose': {'height': '80px', 'input_height': '44px'}
        }

        current_config = spacing_config.get(getattr(self, 'row_spacing', 'dense'))

        # Add a column for delete button
        columns_with_delete = self.columns.copy()
        columns_with_delete.append({
            'name': 'actions',
            'label': '',
            'field': 'actions',
            'align': 'center'
        })

        self.table = ui.table(
            columns=columns_with_delete,
            rows=self.filtered_data,
            row_key='id',
            pagination={'rowsPerPage': 15}
        ).classes('w-full')

        self.table.add_slot('header', '''
            <q-tr>
                <q-th style="width: 50px; padding: 0px 4px"></q-th>
                <q-th v-for="col in props.cols" :key="col.name" 
                     :class="col.headerClass"
                     style="padding: 2px 16px 2px 4px; text-align: left">
                    {{ col.label }}
                </q-th>
            </q-tr>
        ''')

        self.table.add_slot('body', self.get_table_body_template(
            current_config['height'],
            current_config['input_height']
        ))

        # Update event handlers
        self.table.on('update:team_dri', self.update_team_dri)
        self.table.on('row:delete', self.delete_row)
        self.table.on('add:comment', self.add_comment)
        self.table.on('edit:comment', self.edit_comment)

    def update_team_dri(self, e):
        row_id = e.args['id']
        new_team_dri = e.args['value']

        for row in self.data:
            if row['id'] == row_id:
                old_team_dri = row['team_dri']
                row['team_dri'] = new_team_dri
                row['history'].append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'field': 'team_dri',
                    'old_value': old_team_dri,
                    'new_value': new_team_dri
                })
                break

        self.apply_filters()

    def delete_row(self, row_id):
        self.data = [row for row in self.data if row['id'] != row_id.args]
        self.filtered_data = [row for row in self.filtered_data if row['id'] != row_id.args]
        self.update_table()
        self.update_view()
        ui.notify(f'Radar {row_id.args} has been removed')

    def change_row_spacing(self, e):
        if hasattr(self, 'table'):
            self.row_spacing = e.value
            spacing_config = {
                'dense': {'height': '48px', 'input_height': '28px'},  # Better input/row ratio
                'normal': {'height': '64px', 'input_height': '36px'},  # More comfortable input size
                'loose': {'height': '80px', 'input_height': '44px'}  # Reduced from 96px, better scaling
            }
            current_config = spacing_config[e.value]

            # Update the existing table's body slot
            self.table.add_slot('body', self.get_table_body_template(
                current_config['height'],
                current_config['input_height']
            ))
            self.table.update()

    def get_table_body_template(self, row_height, input_height):
        return f'''
               <q-tr :props="props" class="text-xs hover:bg-gray-50" style="height: {row_height}">
                   <!-- Expand button cell -->
                   <q-td style="width: 50px; padding: 0px 4px; text-align: center">
                       <q-btn size="xs" color="blue" round dense flat
                           @click="props.expand = !props.expand"
                           :icon="props.expand ? 'remove' : 'add'" />
                   </q-td>

                   <!-- Data cells -->
                   <q-td v-for="col in props.cols" :key="col.name" :props="props" 
                         style="padding: 2px 16px 2px 4px">
                       <template v-if="col.name === 'id'">
                            <a :href="col.value" 
                               class="text-blue-600 hover:text-blue-800 hover:underline">
                                {{{{ col.value }}}}
                            </a>
                       </template>
                       <template v-else-if="col.name === 'tags'">
                           <div class="flex gap-0.5">
                               <span v-for="tag in col.value" 
                                   :key="tag.text" 
                                   class="px-1 rounded text-xs"
                                   :style="tag.style">
                                   {{{{tag.text}}}}
                               </span>
                           </div>
                       </template>
                       <template v-else-if="col.name === 'team_dri'">
                           <q-select
                               v-model="props.row.team_dri"
                               :options="['Person A', 'Person B', 'Person C', 'Person D', 'Person E']"
                               dense
                               borderless
                               class="text-xs"
                               style="padding: 0; margin: 0; min-height: {input_height};"
                               @update:model-value="$parent.$emit('update:team_dri', 
                                                {{ id: props.row.id, value: $event }})"
                           />
                       </template>
                       <template v-else-if="col.name === 'comments'">
                           <div class="text-xs text-gray-500">
                               {{{{ props.row.comments_history ? props.row.comments_history.length : 0 }}}} comment(s)
                           </div>
                       </template>
                       <template v-else-if="col.name === 'actions'">
                           <q-btn size="xs" color="red" round dense flat icon="delete" class="delete-btn"
                                  @click="$q.dialog({{
                                      title: 'Confirm Deletion',
                                      message: 'Are you sure you want to delete this radar?',
                                      ok: {{ label: 'Yes', color: 'negative' }},
                                      cancel: {{ label: 'Cancel' }}
                                  }}).onOk(() => {{
                                      $parent.$emit('row:delete', props.row.id)
                                  }})" />
                       </template>
                       <template v-else>
                           {{{{ col.value }}}}
                       </template>
                   </q-td>
               </q-tr>
               <q-tr v-show="props.expand" :props="props">
                   <q-td style="width: 50px"></q-td>
                   <q-td colspan="100%">
                       <div class="text-left p-4 bg-gray-50">
                           <!-- Summary Section -->
                           <div class="mb-4">
                               <div class="text-sm font-bold mb-2">Summary</div>
                               <div class="text-xs text-gray-500 italic">TBD - This section will be implemented in future updates.</div>
                           </div>

                           <!-- Comments Section -->
                           <div>
                               <div class="text-sm font-bold mb-2">Comments</div>

                               <!-- Add new comment section -->
                               <div class="mb-4">
                                   <q-input
                                       v-model="props.row.newComment"
                                       type="textarea"
                                       dense
                                       outlined
                                       placeholder="Add a new comment..."
                                       class="text-xs bg-white mb-2"
                                       style="min-height: 60px"
                                   />
                                   <q-btn 
                                       color="primary" 
                                       dense 
                                       size="sm"
                                       :disable="!props.row.newComment"
                                       @click="$parent.$emit('add:comment', {{ 
                                           id: props.row.id, 
                                           comment: props.row.newComment 
                                       }})"
                                   >
                                       Add Comment
                                   </q-btn>
                               </div>

                               <!-- Comments list -->
                               <div class="space-y-2">
                                   <div v-for="(comment, index) in props.row.comments_history" 
                                       :key="comment.id" 
                                       class="bg-white p-3 rounded border"
                                   >
                                       <div class="flex justify-between items-start mb-1">
                                           <div class="text-xs text-gray-500">
                                               {{{{ comment.timestamp }}}} by {{{{ comment.author }}}}
                                           </div>
                                           <div class="flex gap-1">
                                               <q-btn 
                                                   v-if="!comment.editing"
                                                   flat 
                                                   dense 
                                                   round 
                                                   icon="edit" 
                                                   size="xs"
                                                   @click="comment.editing = true; comment.editText = comment.comment"
                                               />
                                               <template v-else>
                                                   <q-btn 
                                                       flat 
                                                       dense 
                                                       round 
                                                       icon="check" 
                                                       size="xs"
                                                       color="positive"
                                                       @click="$parent.$emit('edit:comment', {{ 
                                                           radarId: props.row.id, 
                                                           commentId: comment.id,
                                                           newComment: comment.editText 
                                                       }})"
                                                   />
                                                   <q-btn 
                                                       flat 
                                                       dense 
                                                       round 
                                                       icon="close" 
                                                       size="xs"
                                                       color="negative"
                                                       @click="comment.editing = false"
                                                   />
                                               </template>
                                           </div>
                                       </div>
                                       <div v-if="!comment.editing" class="text-sm whitespace-pre-wrap">
                                           {{{{ comment.comment }}}}
                                       </div>
                                       <q-input
                                           v-else
                                           v-model="comment.editText"
                                           type="textarea"
                                           dense
                                           outlined
                                           autogrow
                                           class="text-sm"
                                       />
                                   </div>
                               </div>
                           </div>
                       </div>
                   </q-td>
               </q-tr>
           '''

    def add_comment(self, e):
        row_id = e.args['id']
        comment_text = e.args['comment']

        for row in self.data:
            if row['id'] == row_id:
                new_comment = {
                    'id': f'comment-{row_id}-{len(row["comments_history"]) + 1}',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'comment': comment_text,
                    'author': 'Current User'  # You can replace this with actual user info
                }
                row['comments_history'].append(new_comment)
                row['newComment'] = ''  # Clear the input field
                break

        self.update_table()
        ui.notify('Comment added successfully')

    def edit_comment(self, e):
        radar_id = e.args['radarId']
        comment_id = e.args['commentId']
        new_comment = e.args['newComment']

        for row in self.data:
            if row['id'] == radar_id:
                for comment in row['comments_history']:
                    if comment['id'] == comment_id:
                        comment['comment'] = new_comment
                        comment['editing'] = False
                        break
                break

        self.update_table()
        ui.notify('Comment updated successfully')

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