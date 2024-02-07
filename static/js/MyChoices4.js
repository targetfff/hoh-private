    const elements = document.querySelectorAll('.options_for_select');
    var lst = [{value: 0, label: 'Без родителя',
                description: 'Категория будет считаться одной из "основных"'}];
    elements.forEach(el => {
        Option = {value: $(el).attr('id'), label: $(el).val()};
        lst.push(Option);
    });
        VirtualSelect.init({
  ele: '#example-select',
  hasOptionDescription: true,
  options: lst,
  search: true,
  name: 'parent',
  placeholder: 'Выберите родителя',
  multiple: false,
  optionsCount: 4,
  optionHeight: '60%',
  required: true,
  selectedValue: 0,
  maxWidth: '100%',
  noOptionsText: 'Пока что категорий нет...',
  noSearchResultsText: 'Ничего не найдено',
  searchPlaceholderText: 'Поиск...',
});