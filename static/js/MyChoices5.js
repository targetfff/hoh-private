    var elements = document.querySelectorAll('.options_for_select');
    var lst = [];
    elements.forEach(el => {
        Option = {value: $(el).attr('id'), label: $(el).val()};
        lst.push(Option);
    });
    var selected_ = document.querySelectorAll('.options_for_select2')
    var selected = []
    selected_.forEach(el => {
        Option = $(el).val();
        selected.push(Option);
    });
        VirtualSelect.init({
  ele: '#example-select',
  options: lst,
  search: true,
  name: 'categories',
  placeholder: 'Выберите категории',
  multiple: true,
  optionsCount: 5,
  optionHeight: '50%',
  required: true,
  selectedValue: selected,
  maxWidth: '100%',
  noOptionsText: 'Пока что категорий нет...',
  noSearchResultsText: 'Ничего не найдено',
  searchPlaceholderText: 'Поиск...',
  allOptionsSelectedText: 'Все',
  optionsSelectedText: 'кат. выбрано',
});